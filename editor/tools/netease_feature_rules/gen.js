const fs = require('fs')

const folders = [ ]
const biomeTags = [ 'overworld', 'overworld_generation' ]
const biomesExclude = [ ]
const startPosition = {
    x: 0,
    z: 0
}
const heightAboveGround = 0

const _biomeFilter = () => {
    const filters = [
        {
            all_of: [
                {
                    any_of: biomeTags.map(tag => ({
                        test: "has_biome_tag",
                        operator: "==",
                        value: tag
                    }))
                },
            ]
        }
    ]

    if (biomesExclude.length > 0) {
        filters[0].all_of.push({
            all_of: biomesExclude.map(tag => ({
                test: "has_biome_tag",
                operator: "!=",
                value: tag
            }))
        })
    }

    return JSON.stringify(filters)
}

const content = (namespace, name, ox, oy) => {
    const sx = startPosition.x + ox
    const sz = startPosition.z + oy
    const modx = sx % 16
    const modz = sz % 16
    const x = sx - modx
    const z = sz - modz
    return `{
  "format_version": "1.14.0",
  "minecraft:feature_rules": {
    "description": {
      "identifier": "${namespace}:${name}",
      "places_feature": "${namespace}:${name}"
    },
    "conditions": {
      "placement_pass": "final_pass",
      "minecraft:biome_filter": ${_biomeFilter()}
    },
    "distribution": {
      "iterations": "variable.originx == ${x} && variable.originz == ${z} ?1:0",
      "coordinate_eval_order": "xzy",
      "scatter_chance": 100.0,
      "x": 0,
      "y": "query.get_height_at(variable.worldx - ${x}, variable.worldz - ${z}) + ${heightAboveGround}",
      "z": 0
    }
  }
}`
}

folders.forEach(folder => {
    const folderPath = `../structures/${folder}`
    fs.readdirSync(folderPath).forEach(file => {
        if (!file.endsWith('.json')) {
            return
        }

        const parts = JSON.parse(fs.readFileSync(`${folderPath}/${file}`).toString())
        const { pos: [ sx, _, sz ] } = parts[0]
        parts.forEach(({ file, pos: [ox, _, oz] }) => {
            if (!fs.existsSync(folder)) {
                fs.mkdirSync(folder)
            }
            const name = file.replace('.mcstructure', '')
            fs.writeFileSync(`${folder}/${name}.json`, content(folder, name, ox - sx, oz - sz))
        })
    })
})