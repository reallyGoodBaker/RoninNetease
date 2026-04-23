const fs = require('fs')
const path = require('path')

const moduleDir = path.resolve(__dirname, '../../../../')

function findResDir() {
    for (const dir of fs.readdirSync(moduleDir)) {
        const filePath = path.join(moduleDir, dir)
        if (fs.statSync(filePath).isDirectory()) {
            const manifest = findManifest(filePath)
            if (manifest) {
                return manifest
            }
        }
    }
}

function findManifest(filePath) {
    const manifestPath = path.join(filePath, 'manifest.json')
    if (!fs.existsSync(manifestPath)) {
        return
    }

    const manifest = JSON.parse(fs.readFileSync(manifestPath, 'utf8'))
    for (const { type } of manifest.modules) {
        if (type === 'resources') {
            return filePath
        }
    }
}


function walkDir(dir, callback) {
    fs.readdirSync(dir).forEach((file) => {
        const filePath = path.join(dir, file)
        if (fs.statSync(filePath).isDirectory()) {
            walkDir(filePath, callback)
        } else {
            callback(filePath)
        }
    })
}


function findAnimResources(resDir, consumer) {
    const animDir = path.join(resDir, 'animations')
    walkDir(animDir, filePath => {
        if (path.extname(filePath) != '.json') {
            return
        }

        const anim = JSON.parse(fs.readFileSync(filePath, 'utf8'))
        consumer(anim)
    })
}


function extractAnimations() {
    const resDir = findResDir()
    if (!resDir) {
        console.error('Cannot find resources directory')
        return
    }

    const animMetaPath = path.join(__dirname, '../../assets/animMeta.py')
    const animMetaInfos = {}

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

    // Merge anim resources
    findAnimResources(resDir, ({ animations }) => {
        for (const [ key, { loop, animation_length } ] of Object.entries(animations)) {
            animMetaInfos[key] = {
                loop,
                length: animation_length
            }
        }
    })

    fs.writeFileSync(
        animMetaPath,
        `AnimMeta = ${JSON.stringify(animMetaInfos, null, 4)}`
            .replaceAll('true', 'True')
            .replaceAll('false', 'False')
    )
}

extractAnimations()