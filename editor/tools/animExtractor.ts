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


function findAnimResources(resDir: string, consumer: (obj: any) => void) {
    const animDir = path.join(resDir, 'animations')
    walkDir(animDir, filePath => {
        if (path.extname(filePath) != '.json') {
            return
        }

        const anim = JSON.parse(fs.readFileSync(filePath, 'utf8'))
        consumer(anim)
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


function extractAnimations() {
    const resDir = findResDir()
    if (!resDir) {
        console.error('Cannot find resources directory')
        return
    }

    const animMetaPath = path.join(import.meta.dirname, './animMeta.py')
    const animMetaInfos = {} as any

    if (fs.existsSync(animMetaPath)) {
        const existedMeta = JSON.parse(
            fs.readFileSync(animMetaPath).toString()
                .replace('AnimMeta = ', '')
                .replaceAll('True', 'true')
                .replaceAll('False', 'false')
            )
        for (const [ key, value ] of Object.entries(existedMeta)) {
            animMetaInfos[key] = value
        }
    }

    const animKeys = [] as any[]

    // Merge anim resources
    findAnimResources(resDir, ({ animations }: { animations: { loop: any, animation_length: any, timeline: any } }) => {
        for (const [ key, { loop, animation_length, timeline } ] of Object.entries(animations)) {
            const metaInfo = {
                loop: loop ?? false,
                length: animation_length ?? -1,
            }
            handleExtraData(metaInfo, timeline)
            animMetaInfos[key] = metaInfo
            if (animKeys.includes(key)) {
                console.error(`Conflict animations: ${key}`)
            }
            animKeys.push(key)
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