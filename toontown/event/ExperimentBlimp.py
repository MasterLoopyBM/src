from direct.actor.Actor import Actor
from direct.distributed.ClockDelta import globalClockDelta
from direct.fsm.FSM import FSM
from direct.interval.IntervalGlobal import Func
from direct.interval.IntervalGlobal import Sequence, LerpHprInterval, Wait
from panda3d.core import NodePath, Vec3, Texture

from otp.ai.MagicWordGlobal import *
from toontown.suit.BossCog import BossCog
from toontown.suit.SuitDNA import SuitDNA


STATIC_SCREEN_INDEX = 0
CHAIRMAN_SCREEN_INDEX = 1
BOSSBOT_SCREEN_INDEX = 2
LAWBOT_SCREEN_INDEX = 3
CASHBOT_SCREEN_INDEX = 4
SELLBOT_SCREEN_INDEX = 5


class BossbotScene(NodePath):
    def __init__(self):
        NodePath.__init__(self, 'BossbotScene')

        self.background = loader.loadModel('phase_12/models/bossbotHQ/BanquetInterior_1.bam')
        self.background.reparentTo(self)

        self.boss = BossCog()
        dna = SuitDNA()
        dna.newBossCog('c')
        self.boss.setDNA(dna)
        self.boss.reparentTo(self)
        self.boss.setPos(0, 236.89, 0)
        self.boss.loop('neutral')

    def delete(self):
        if self.boss is not None:
            self.boss.delete()
            self.boss = None

        if self.background is not None:
            self.background.removeNode()
            self.background = None

        NodePath.removeNode(self)


class LawbotScene:
    def delete(self):
        pass


class CashbotScene:
    def delete(self):
        pass


class SellbotScene:
    def delete(self):
        pass


class ExperimentBlimp(Actor, FSM):
    notify = directNotify.newCategory('ExperimentBlimp')

    def __init__(self):
        Actor.__init__(self, None, None, None, flattenable=0, setFinal=1)
        FSM.__init__(self, 'ExperimentBlimp')

        self.bossbotScene = BossbotScene()
        self.lawbotScene = LawbotScene()
        self.cashbotScene = CashbotScene()
        self.sellbotScene = SellbotScene()

        self.loadModel('phase_4/models/events/blimp_mod.bam')
        self.loadAnims({'flying': 'phase_4/models/events/blimp_chan_flying.bam'})

        self.tv = loader.loadModel('phase_4/models/events/blimp_tv.bam')
        self.tv.reparentTo(self)

        self.staticScreenTex = loader.loadTexture('phase_4/maps/blimp_tv_map_01.png')
        self.staticScreenTex.setMinfilter(Texture.FTLinearMipmapLinear)
        self.staticScreenTex.setMagfilter(Texture.FTLinear)

        self.chairmanScreenTex = loader.loadTexture('phase_4/maps/blimp_tv_map_CM.png')
        self.chairmanScreenTex.setMinfilter(Texture.FTLinearMipmapLinear)
        self.chairmanScreenTex.setMagfilter(Texture.FTLinear)

        self.buffer = base.win.makeTextureBuffer('tv', 960, 540)
        self.buffer.setSort(-100)

        self.camera = base.makeCamera(self.buffer)

        self.tvIval = None

        self.flyTrack = Sequence(
            LerpHprInterval(self, 3.5, Vec3(140, 0, 5),
                            startHpr=Vec3(140, 0, -5), blendType='easeInOut',
                            fluid=1),
            LerpHprInterval(self, 3.5, Vec3(140, 0, -5),
                            startHpr=Vec3(140, 0, 5), blendType='easeInOut',
                            fluid=1)
        )

    def cleanup(self):
        if self.flyTrack is not None:
            self.stopFlying()
            self.flyTrack = None

        if self.tvIval is not None:
            self.tvIval.finish()
            self.tvIval = None

        if self.camera is not None:
            self.camera.removeNode()
            self.camera = None

        if self.buffer is not None:
            base.graphicsEngine.removeWindow(self.buffer)
            self.buffer = None

        if self.chairmanScreenTex is not None:
            self.chairmanScreenTex.clear()
            self.chairmanScreenTex = None

        if self.staticScreenTex is not None:
            self.staticScreenTex.clear()
            self.staticScreenTex = None

        if self.tv is not None:
            self.tv.removeNode()
            self.tv = None

        if self.sellbotScene is not None:
            self.sellbotScene.delete()
            self.sellbotScene = None

        if self.cashbotScene is not None:
            self.cashbotScene.delete()
            self.cashbotScene = None

        if self.lawbotScene is not None:
            self.lawbotScene.delete()
            self.lawbotScene = None

        if self.bossbotScene is not None:
            self.bossbotScene.delete()
            self.bossbotScene = None

        Actor.cleanup(self)

    def enterPhase0(self, timestamp):
        """
        Phase 0 describes the blimp when it is almost always displaying a
        static image on its monitor. It will, however, flash a drawing of the
        Chairman every 45 seconds.
        """
        self.tvIval = Sequence(
            Wait(45),
            Func(self.setScreen, CHAIRMAN_SCREEN_INDEX),
            Wait(0.25),
            Func(self.setScreen, STATIC_SCREEN_INDEX),
            Wait(0.5),
            Func(self.setScreen, CHAIRMAN_SCREEN_INDEX),
            Wait(0.1),
            Func(self.setScreen, STATIC_SCREEN_INDEX),
            Wait(0.1),
            Func(self.setScreen, CHAIRMAN_SCREEN_INDEX),
            Wait(0.1),
            Func(self.setScreen, STATIC_SCREEN_INDEX)
        )
        self.tvIval.loop(globalClockDelta.localElapsedTime(timestamp, bits=32))

    def exitPhase0(self):
        if self.tvIval is not None:
            self.tvIval.finish()
            self.tvIval = None

    def enterPhase1(self, timestamp):
        """
        Phase 1 describes the blimp when it is constantly flickering between
        the first four boss Cogs (the Sellbot V.P., the Cashbot C.F.O., the
        Lawbot C.J., and the Bossbot C.E.O.). They will be standing still in a
        neutral animation inside of their respective headquarters.
        """
        self.setScreen(BOSSBOT_SCREEN_INDEX)

    def enterPhase2(self, timestamp):
        """
        Phase 2 describes the blimp in the same state as phase 1, however, the
        boss Cogs' subordinates have joined in on the spectating.
        """
        pass

    def enterPhase3(self, timestamp):
        """
        Phase 3 describes the blimp in the same state as phase 2, however, the
        both the boss Cogs, and their subordinates are cheering over the
        destruction of Toontown Central.
        """
        pass

    def startFlying(self, timestamp):
        self.loop('flying')
        self.flyTrack.loop(globalClockDelta.localElapsedTime(timestamp, bits=32))

    def stopFlying(self):
        self.flyTrack.finish()
        self.stop()

    def setScreen(self, screenIndex):
        tvScreen = self.tv.find('**/tv_screen')
        ts = tvScreen.findTextureStage('*')
        if screenIndex == STATIC_SCREEN_INDEX:
            tvScreen.setTexScale(ts, 1, 1)
            tvScreen.setTexture(ts, self.staticScreenTex, 1)
        elif screenIndex == CHAIRMAN_SCREEN_INDEX:
            tvScreen.setTexScale(ts, 1, 1)
            tvScreen.setTexture(ts, self.chairmanScreenTex, 1)
        elif screenIndex == BOSSBOT_SCREEN_INDEX:
            tvScreen.setTexScale(ts, 1, 1.15)
            self.camera.reparentTo(self.bossbotScene)
            self.camera.setPosHpr(0, 203.5, 23.5, 0, 354, 0)
            tvScreen.setTexture(ts, buffer.getTexture(), 1)
        elif screenIndex == LAWBOT_SCREEN_INDEX:
            tvScreen.setTexScale(ts, 1, 1.15)
            self.camera.reparentTo(self.lawbotScene)
            self.camera.setPosHpr(-3.84, -29.84, 93.08, 0, 348, 0)
            tvScreen.setTexture(ts, buffer.getTexture(), 1)
        elif screenIndex == CASHBOT_SCREEN_INDEX:
            tvScreen.setTexScale(ts, 1, 1.15)
            self.camera.reparentTo(self.cashbotScene)
            tvScreen.setTexture(ts, buffer.getTexture(), 1)
        elif screenIndex == SELLBOT_SCREEN_INDEX:
            tvScreen.setTexScale(ts, 1, 1.15)
            self.camera.reparentTo(self.sellbotScene)
            tvScreen.setTexture(ts, buffer.getTexture(), 1)


@magicWord(category=CATEGORY_PROGRAMMER, types=[int])
def blimp(phase):
    if not (0 <= phase <= 3):
        return 'Invalid phase.'
    for event in base.cr.doFindAll('DistributedExperimentEvent'):
        event.blimp.request('Phase%d' % phase, 0)
        break
    else:
        return "Couldn't find a blimp."