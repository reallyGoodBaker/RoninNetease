# -*- coding: utf-8 -*-
"""
动画变量命名规范（唯一规则）：

    动画名去掉 "animation." 前缀后，把 "." 全部替换成 "_"

    animation.template.pistol.aim_shoot
        -> template_pistol_aim_shoot

混合权重变量：v.blend_template_pistol_aim_shoot
动画时间变量：v.anim_time_template_pistol_aim_shoot

动画文件里：
    blend_weight 写成 v.blend_xxx ?? 1（Blockbench 预览默认 1）
    anim_time_update 写成 v.anim_time_xxx（不写 ?? 1）
游戏端条件仍用 v.blend_xxx ?? 0，避免未注册变量误播放。
"""


def _flat(animName):
    # type: (str) -> str
    return animName.replace('animation.', '').replace('.', '_')


def blendVar(animName):
    # type: (str) -> str
    return 'blend_' + _flat(animName)


def blendVarMolang(animName):
    # type: (str) -> str
    return 'v.' + blendVar(animName)


def animTimeVar(animName):
    # type: (str) -> str
    return 'anim_time_' + _flat(animName)


def animTimeVarMolang(animName):
    # type: (str) -> str
    return 'v.' + animTimeVar(animName)
