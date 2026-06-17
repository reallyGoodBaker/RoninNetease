import path from 'path'
import * as fs from 'fs'


const moduleDir = path.resolve(import.meta.dirname, '../../../../../')
console.log('Module directory:', moduleDir)

export function findResDir() {
    for (const dir of fs.readdirSync(moduleDir)) {
        const filePath = path.join(moduleDir, dir)
        if (fs.statSync(filePath).isDirectory()) {
            const manifest = findManifest(filePath, 'resources')
            if (manifest) {
                return manifest
            }
        }
    }
}

export function findDataDir() {
    for (const dir of fs.readdirSync(moduleDir)) {
        const filePath = path.join(moduleDir, dir)
        if (fs.statSync(filePath).isDirectory()) {
            const manifest = findManifest(filePath, 'data')
            if (manifest) {
                return manifest
            }
        }
    }
}


export function findManifest(filePath: string, moduleType: 'resources' | 'data') {
    const manifestPath = path.join(filePath, 'manifest.json')
    if (!fs.existsSync(manifestPath)) {
        return
    }

    const manifest = JSON.parse(fs.readFileSync(manifestPath, 'utf8'))
    for (const { type } of manifest.modules) {
        if (type === moduleType) {
            return filePath
        }
    }
}