from ...subsystem import ClientSubsystem, SubsystemClient
from ...component import ClientComponent, Component, createComponent, getOneComponent
from ...basic import compClient, clientApi
from ...event.client import EventListener
from mod.common.minecraftEnum import EntityType
import time

PlayerDefaultClientDef = {
    "materials": {
        "default": "entity_alphatest",
        "cape": "entity_alphatest",
        "animated": "player_animated",
        "spectator": "player_spectator"
    },
    "textures": {
        "default": "textures/entity/steve",
        "cape": "textures/entity/cape_invisible"
    },
    "geometry": {
        "default": "geometry.humanoid.custom",
        "cape": "geometry.cape"
    },
    "scripts": {
        "animate": [
            "root"
        ]
    },
    "animations": {
        "root": "controller.animation.player.root",
        "base_controller": "controller.animation.player.base",
        "hudplayer": "controller.animation.player.hudplayer",
        "humanoid_base_pose": "animation.humanoid.base_pose",
        "look_at_target": "controller.animation.humanoid.look_at_target",
        "look_at_target_ui": "animation.player.look_at_target.ui",
        "look_at_target_default": "animation.humanoid.look_at_target.default",
        "look_at_target_gliding": "animation.humanoid.look_at_target.gliding",
        "look_at_target_swimming": "animation.humanoid.look_at_target.swimming",
        "look_at_target_inverted": "animation.player.look_at_target.inverted",
        "cape": "animation.player.cape",
        "move.arms": "animation.player.move.arms",
        "move.legs": "animation.player.move.legs",
        "swimming": "animation.player.swim",
        "swimming.legs": "animation.player.swim.legs",
        "riding.arms": "animation.player.riding.arms",
        "riding.legs": "animation.player.riding.legs",
        "holding": "animation.player.holding",
        "brandish_spear": "animation.humanoid.brandish_spear",
        "charging": "animation.humanoid.charging",
        "attack.positions": "animation.player.attack.positions",
        "attack.rotations": "animation.player.attack.rotations",
        "sneaking": "animation.player.sneaking",
        "bob": "animation.player.bob",
        "damage_nearby_mobs": "animation.humanoid.damage_nearby_mobs",
        "bow_and_arrow": "animation.humanoid.bow_and_arrow",
        "use_item_progress": "animation.humanoid.use_item_progress",
        "skeleton_attack": "animation.skeleton.attack",
        "sleeping": "animation.player.sleeping",
        "first_person_base_pose": "animation.player.first_person.base_pose",
        "first_person_empty_hand": "animation.player.first_person.empty_hand",
        "first_person_swap_item": "animation.player.first_person.swap_item",
        "first_person_attack_controller": "controller.animation.player.first_person_attack",
        "first_person_attack_rotation": "animation.player.first_person.attack_rotation",
        "first_person_attack_rotation_item": "animation.player.first_person.attack_rotation_item",
        "first_person_vr_attack_rotation": "animation.player.first_person.vr_attack_rotation",
        "first_person_walk": "animation.player.first_person.walk",
        "first_person_map_controller": "controller.animation.player.first_person_map",
        "first_person_map_hold": "animation.player.first_person.map_hold",
        "first_person_map_hold_attack": "animation.player.first_person.map_hold_attack",
        "first_person_map_hold_off_hand": "animation.player.first_person.map_hold_off_hand",
        "first_person_map_hold_main_hand": "animation.player.first_person.map_hold_main_hand",
        "first_person_crossbow_equipped": "animation.player.first_person.crossbow_equipped",
        "first_person_crossbow_hold": "animation.player.first_person.crossbow_hold",
        "first_person_breathing_bob": "animation.player.first_person.breathing_bob",
        "third_person_crossbow_equipped": "animation.player.crossbow_equipped",
        "third_person_bow_equipped": "animation.player.bow_equipped",
        "crossbow_hold": "animation.player.crossbow_hold",
        "crossbow_controller": "controller.animation.player.crossbow",
        "shield_block_main_hand": "animation.player.shield_block_main_hand",
        "shield_block_off_hand": "animation.player.shield_block_off_hand",
        "blink": "controller.animation.persona.blink",
        "fishing_rod": "animation.humanoid.fishing_rod",
        "holding_spyglass": "animation.humanoid.holding_spyglass",
        "first_person_shield_block": "animation.player.first_person.shield_block",
        "tooting_goat_horn": "animation.humanoid.tooting_goat_horn",
        "holding_brush": "animation.humanoid.holding_brush",
        "brushing": "animation.humanoid.brushing",
        "crawling": "animation.player.crawl",
        "crawling.legs": "animation.player.crawl.legs"
    },
    "render_controllers": [
        {
            "controller.render.player.first_person_spectator": "variable.is_first_person && query.is_spectator"
        },
        {
            "controller.render.player.third_person_spectator": "!variable.is_first_person && !variable.map_face_icon && query.is_spectator"
        },
        {
            "controller.render.player.first_person": "variable.is_first_person && !query.is_spectator"
        },
        {
            "controller.render.player.third_person": "!variable.is_first_person && !variable.map_face_icon && !query.is_spectator"
        },
        {
            "controller.render.player.map": "variable.map_face_icon"
        }
    ],
}

class PlayerResPreload:

    def __init__(self, id, geometry={}, animations={}, textures={}, materials={}):
        self.preloadObject = {
            "geometry": geometry,
            "animations": animations,
            "textures": textures,
            "materials": materials,
        }
        self.id = id

    @staticmethod
    def key(id):
        return id.replace(':', '.')

@Component()
class PersonaRendererComponent(ClientComponent):
    def onCreate(self, entityId):
        self.entityId = entityId
        self.actorRenderer = compClient.CreateActorRender(entityId)
        self.override = None
        self.playerPreloads = set()
        self.modified = False
        self.molang = compClient.CreateQueryVariable(entityId)
        self.molang.Register('query.mod.player_preload', -1)

    def broadcastRenderConf(self, subSys, jsonObj={}):
        subSys.sendServer('PersonaChangeClient', { 'id': self.entityId, 'data': jsonObj })

    def broadcastResetConf(self, subSys):
        subSys.sendServer('PersonaResetClient', { 'id': self.entityId })

    def changeActorRenderConf(self, jsonObject, actor=None):
        # type: (dict, str) -> None

        actorId = actor or self.entityId
        # 材质
        materials = jsonObject.get("materials")
        if materials:
            for name, material in materials.items():
                self.actorRenderer.AddRenderMaterialToOneActor(actorId, name, material)

        # 模型
        geometries = jsonObject.get("geometry")
        if geometries:
            for name, geometry in geometries.items():
                self.actorRenderer.AddGeometryToOneActor(actorId, name, geometry)

        # 贴图
        textures = jsonObject.get("textures")
        if textures:
            for name, texture in textures.items():
                self.actorRenderer.AddTextureToOneActor(actorId, name, texture)

        # 动画/动画控制器
        animations = jsonObject.get("animations")
        if animations:
            for name, animation in animations.items():
                if animation.startswith('controller.'):
                    self.actorRenderer.AddAnimationControllerToOneActor(actorId, name, animation)
                else:
                    self.actorRenderer.AddAnimationToOneActor(actorId, name, animation)

        # 粒子
        particles = jsonObject.get("particle_effects")
        if particles:
            for name, particle in particles.items():
                self.actorRenderer.AddParticleEffectToOneActor(actorId, name, particle)

        # 渲染控制器
        renderControllers = jsonObject.get("render_controllers")
        if renderControllers:
            for renderControllerDef in renderControllers:
                if isinstance(renderControllerDef, dict):
                    name, cond = renderControllerDef.items()[0]
                    self.actorRenderer.AddRenderControllerToOneActor(actorId, name, cond)
                else:
                    self.actorRenderer.AddRenderControllerToOneActor(actorId, renderControllerDef)

        # scripts
        scripts = jsonObject.get("scripts")
        if scripts:
            animates = scripts.get('animate')
            if animates:
                for animate in animates:
                    if isinstance(animate, dict):
                        name, cond = animate.items()[0]
                        self.actorRenderer.AddScriptAnimateToOneActor(actorId, name, cond)
                    else:
                        self.actorRenderer.AddScriptAnimateToOneActor(actorId, animate)

        self.actorRenderer.RebuildRenderForOneActor()
        self.modified = True

    def changePlayerRenderConf(self, jsonObject={}):
        # type: (dict) -> None

        overrideObj = {
            'geo': [],
            'animController': [],
            'renderController': [],
        }

        # 材质
        materials = jsonObject.get("materials")
        if materials:
            for name, material in materials.items():
                self.actorRenderer.AddPlayerRenderMaterial(name, material)

        # 模型
        geometries = jsonObject.get("geometry")
        if geometries:
            for name, geometry in geometries.items():
                overrideObj['geo'].append(name)
                self.actorRenderer.AddPlayerGeometry(name, geometry)

        # 贴图
        textures = jsonObject.get("textures")
        if textures:
            for name, texture in textures.items():
                self.actorRenderer.AddPlayerTexture(name, texture)

        # 动画/动画控制器
        animations = jsonObject.get("animations")
        if animations:
            for name, animation in animations.items():
                if animation.startswith('controller.'):
                    overrideObj['animController'].append(name)
                    self.actorRenderer.AddPlayerAnimationController(name, animation)
                else:
                    self.actorRenderer.AddPlayerAnimation(name, animation)

        # 粒子
        particles = jsonObject.get("particle_effects")
        if particles:
            for name, particle in particles.items():
                self.actorRenderer.AddPlayerParticleEffect(name, particle)

        # 渲染控制器
        renderControllers = jsonObject.get("render_controllers")
        if renderControllers:
            for renderControllerDef in renderControllers:
                if isinstance(renderControllerDef, dict):
                    name, cond = renderControllerDef.items()[0]
                    overrideObj['renderController'].append(name)
                    self.actorRenderer.AddPlayerRenderController(name, cond)
                else:
                    overrideObj['renderController'].append(renderControllerDef)
                    self.actorRenderer.AddPlayerRenderController(renderControllerDef)

        # scripts
        scripts = jsonObject.get("scripts")
        if scripts:
            animates = scripts.get('animate')
            if animates:
                for animate in animates:
                    if isinstance(animate, dict):
                        name, cond = animate.items()[0]
                        self.actorRenderer.AddPlayerScriptAnimate(name, cond)
                    else:
                        self.actorRenderer.AddPlayerScriptAnimate(animate)

        self.actorRenderer.RebuildPlayerRender()
        self.modified = True
        self.override = overrideObj

    def showHand(self, visible=True, mode=0):
        self.actorRenderer.SetPlayerItemInHandVisible(visible, mode)

    def changeRenderConf(self, jsonObject):
        if compClient.CreateEngineType(self.entityId).GetEngineType() == EntityType.Player:
            self.changePlayerRenderConf(jsonObject)
        else:
            self.changeActorRenderConf(jsonObject) 

    def resetActorRenderConf(self):
        if not self.modified:
            return

        self.actorRenderer.ResetRenderForOneActor()
        self.modified = False

    def resetPlayerRenderConf(self):
        if not self.modified:
            return

        renderer = self.actorRenderer
        if self.override:
            geos = self.override['geo']
            animControllers = self.override['animController']
            renderControllers = self.override['renderController']
            for anim in animControllers:
                renderer.RemovePlayerAnimationController(anim)

            for geo in geos:
                renderer.RemovePlayerGeometry(geo)

            for renderController in renderControllers:
                renderer.RemovePlayerRenderController(renderController)

        renderer.AddPlayerAnimationController('root', 'controller.animation.player.root')
        renderer.RebuildPlayerRender()
        self.modified = False
        self.override = None

    def resetRenderConf(self):
        if compClient.CreateEngineType(self.entityId).GetEngineType() == EntityType.Player:
            self.resetPlayerRenderConf()
        else:
            self.resetActorRenderConf()

    def addPlayerPreload(self, preload, partVisibility=[{ '*': True }]):
        # type: (PlayerResPreload, list[dict[str, bool]]) -> None
        self.playerPreloads.add(preload)
        jsonObject = preload.preloadObject
        preloadIndex = str(preload.index)
        key = "controller.render.preload.{}".format(preload.id)
        # 模型
        geometries = jsonObject.get("geometry")
        if geometries:
            for name, geometry in geometries.items():
                self.actorRenderer.AddPlayerGeometry(name + '_' + preloadIndex, geometry)

        # 贴图
        textures = jsonObject.get("textures")
        if textures:
            for name, texture in textures.items():
                self.actorRenderer.AddPlayerTexture(name + '_' + preloadIndex, texture)

        # 动画/动画控制器
        animations = jsonObject.get("animations")
        if animations:
            for name, animation in animations.items():
                if animation.startswith('controller.'):
                    self.actorRenderer.AddPlayerAnimationController(name + '_' + preloadIndex, animation)
                else:
                    self.actorRenderer.AddPlayerAnimation(name + '_' + preloadIndex, animation)

    def removePlayerPreload(self, preload):
        # type: (PlayerResPreload) -> None
        self.playerPreloads.remove(preload)
        self.resetPlayerRenderConf()
        self.actorRenderer.RemovePlayerRenderController(
            "controller.render.preload.{}".format(preload.id)
        )

    def changePlayerPreload(self, id):
        # type: (PlayerResPreload) -> None
        for preload in self.playerPreloads:
            if preload.id == id:
                self.molang.Set('query.mod.player_preload', preload.index)
                return

    def addPlayerPreloadMapping(self, mapping, partVisibility=[{ '*': True }]):
        renderCon = {}
        for k, v in mapping.items():
            geo = v.get('geometry', {})
            anim = v.get('animations', {})
            tex = v.get('textures', {})
            mat = v.get('materials', {})
            preload = PlayerResPreload(k.replace(':', '.'), geo, anim, tex, mat)
            self.addPlayerPreload(preload, partVisibility)
        return renderCon


def createPersona(id):
    return createComponent(id, PersonaRendererComponent)

def getPersona(id):
    return getOneComponent(id, PersonaRendererComponent)


@SubsystemClient
class PersonaEventsSubsystem(ClientSubsystem):

    @EventListener('PersonaChangeServer', isCustomEvent=True)
    def onPersonaChangeServer(self, event):
        if not event.id:
            return
        personaRenderer = getPersona(event.id) # type: PersonaRendererComponent
        if personaRenderer:
            personaRenderer.changeRenderConf(event.data)

    @EventListener('PersonaResetServer', isCustomEvent=True)
    def onPersonaResetServer(self, event):
        personaRenderer = getPersona(event.id) # type: PersonaRendererComponent
        if personaRenderer:
            personaRenderer.resetRenderConf()

    @EventListener('PlayerPreloadMappingAddServer', isCustomEvent=True)
    def onPersonaPreloadAddServer(self, event):
        personaRenderer = getPersona(event.id) # type: PersonaRendererComponent
        if personaRenderer:
            personaRenderer.addPlayerPreloadMapping(event.mapping)

    @EventListener('PlayerPreloadSetServer', isCustomEvent=True)
    def onPersonaPreloadSetServer(self, event):
        personaRenderer = getPersona(event.id) # type: PersonaRendererComponent
        if personaRenderer:
            personaRenderer.changePlayerPreload(event.preloadId)