import path from 'path'
import * as fs from 'fs'
import { findResDir } from './utils.ts'


function walkDir(dir: string, callback: (fp: string) => void) {
    fs.readdirSync(dir).forEach((file) => {
        const filePath = path.join(dir, file)
        if (fs.statSync(filePath).isDirectory()) {
            walkDir(filePath, callback)
        } else {
            callback(filePath)
        }
    })
}


function findAnimResources(resDir: string, consumer: (filePath: string, obj: any) => void) {
    const animDir = path.join(resDir, 'animations')
    walkDir(animDir, filePath => {
        if (!filePath.endsWith('.animation_clip.json')) {
            return
        }

        const anim = JSON.parse(fs.readFileSync(filePath, 'utf8'))
        consumer(filePath, anim)
    })
}


function handleExtraData(animMeta: any, timeline: Record<string, string>) {
    if (!timeline) {
        return
    }

    animMeta.notifies = {}
    animMeta.extra = {}
    for (const [ time, expr ] of Object.entries(timeline)) {
        const notifies = []
        const extra = {} as any
        const exprStr = Array.isArray(expr) ? expr.join('') : expr
        for (const equalExpr of exprStr.slice(0, -1).replaceAll(' ', '').split(';')) {
            const [ key, value ] = equalExpr.split('=') as [string, string]
            const variableName = key.replace('v.', '').replace('variable.', '')
            if (variableName.startsWith('notify_')) {
                const notifyName = variableName.slice(7)
                notifies.push({
                    name: notifyName,
                    state: Math.round(Number(value))
                })
            }
            if (variableName.startsWith('data_')) {
                const dataName = variableName.slice(5)
                extra[dataName] = value
            }
        }
        if (notifies.length > 0) {
            animMeta.notifies[time] = notifies
        }
        if (Object.keys(extra).length > 0) {
            animMeta.extra[time] = extra
        }
    }
}


function flatAnimKey(key: string): string {
    return key.replace(/^animation\./, '').replace(/\./g, '_')
}

function extractAnimations() {
    const resDir = findResDir()
    if (!resDir) {
        console.error('Cannot find resources directory')
        return
    }

    const animMetaPath = path.join(import.meta.dirname, './animMeta.py')
    const animMetaInfos = {} as any

    if (fs.existsSync(animMetaPath)) {
        const rawMeta = fs.readFileSync(animMetaPath).toString()
            .replace(/^#.*$/gm, '')
            .replace('AnimMeta = ', '')
            .replaceAll('True', 'true')
            .replaceAll('False', 'false')
        const existedMeta = JSON.parse(rawMeta)
        for (const [ key, value ] of Object.entries(existedMeta)) {
            animMetaInfos[key] = value
        }
    }

    const animKeys = [] as any[]

    // Merge anim resources
    findAnimResources(resDir, (filePath, animJson) => {
        let changed = false
        const animations = animJson.animations || {}
        for (const [ key, anim ] of Object.entries(animations)) {
            const flat = flatAnimKey(key)
            const animTimeVar = 'v.anim_time_' + flat
            const blendVar = 'v.blend_' + flat

            // 必须为每个动画补上 anim_time_update / blend_weight，
            // 否则动画不会读取 v.anim_time_* / v.blend_*，缓动和动画时间都会失效
            if (anim.anim_time_update !== animTimeVar) {
                anim.anim_time_update = animTimeVar
                changed = true
            }
            if (anim.blend_weight !== (blendVar + ' ?? 1')) {
                anim.blend_weight = blendVar + ' ?? 1'
                changed = true
            }

            const metaInfo = {
                loop: anim.loop ?? false,
                length: anim.animation_length ?? -1,
            }
            handleExtraData(metaInfo, anim.timeline)
            animMetaInfos[key] = metaInfo
            if (animKeys.includes(key)) {
                console.error(`Conflict animations: ${key}`)
            }
            animKeys.push(key)
        }
        if (changed) {
            fs.writeFileSync(filePath, JSON.stringify(animJson, null, 4))
            console.log('Auto-filled animation variables:', filePath)
        }
    })

    fs.writeFileSync(
        animMetaPath,
        `# -*- coding: utf-8 -*-\nAnimMeta = ${JSON.stringify(animMetaInfos, null, 4)}`
            .replaceAll('true', 'True')
            .replaceAll('false', 'False')
    )


    console.log('Extracted animations:', animKeys.length)
}

extractAnimations()