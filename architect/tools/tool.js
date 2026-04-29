const fs = require('fs')
const path = require('path')
const proc = require('child_process')

const rootDir = path.join(__dirname, '../../')
const resDir = rootDir
const dataDir = rootDir

const args = process.argv.slice(2)

proc.execSync(`node ./architect/tools/${args[0]} ${args.slice(1).join(' ')}`)