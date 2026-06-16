const fs = require('fs')

const folders = []
const content = (namespace, name) => `{
  "format_version": "1.14.0",
  "netease:structure_feature": {
  "rotation":0,
    "description": {
      "identifier": "${namespace}:${name}"
    },
    "places_structure": "${namespace}:${name}"
  }
}`

folders.forEach(namespace => {
    fs.readdirSync('../structures/' + namespace).forEach(file => {
        if (file.endsWith('.json')) {
            return
        }
        const name = file.replace('.mcstructure', '')
        fs.writeFileSync(`./${name}.json`, content(namespace, name))
    })
})