from tvboxcore.xbmcutils import XBMCUtils
from tvboxcore import logger

import xbmcgui

from window.WindowActions import * #all integer actions

class DefaultWindow(xbmcgui.WindowDialog): #xbmcgui.Window #xbmcgui.Window

    DefaultNoteImage = "default note image"

    scr={}
    scr['L']=0
    scr['T']=0
    scr['W']=1280
    scr['H']=720

    def __init__(self,noteType='t',noteMessage='',noteImage='',L=140,T=110,W=1000,H=500,Font='font14',TxtColor='0xFF64d1ff',logo='',firstButtonText="Ok",secondButtonText="Cancel"):

        if len(noteImage)==0:
            noteImage=DefaultWindow.DefaultNoteImage
        if (noteType.lower()=='text')  or (noteType.lower()=='t'):
            noteType='t'
        elif (noteType.lower()=='image') or (noteType.lower()=='i'):
            noteType='i'
        self.noteType=noteType
        self.noteMessage=noteMessage
        self.noteImage=noteImage
        self.Font=Font
        self.TxtColor=TxtColor

        self.background=XBMCUtils.getAddonFilePath('resources/images/ContentPanel.png')
        self.BG=xbmcgui.ControlImage(L,T,W,H,self.background,aspectRatio=0,colorDiffuse='0xFF3030FF')

        if logo == '':
            logo = XBMCUtils.getAddonFilePath('icon.png')

        iLogoW=68
        iLogoH=68

        self.iLogo=xbmcgui.ControlImage((L+(W/2))-(iLogoW/2),T+10,iLogoW,iLogoH,logo,aspectRatio=0)

        L2=200
        T2=200
        W2=880
        H2=340
        L3=L2+5
        T3=T2+60
        W3=W2-18
        H3=H2-5-60
        self.ImgMessage=xbmcgui.ControlImage(L2,T2,W2,H2,self.noteImage,aspectRatio=0)
        self.TxtMessage=xbmcgui.ControlTextBox(L2+5,T2,W2-10,H2,font=self.Font,textColor=self.TxtColor)

        focus=XBMCUtils.getAddonFilePath('resources/images/button-focus_lightblue.png')
        nofocus=XBMCUtils.getAddonFilePath('resources/images/button-focus_grey.png')

        w1=120
        h1=35
        w2=160
        h2=35
        spacing1=20

        l2=L+W-spacing1-w2
        t2=T+H-h2-spacing1
        l1=L+W-spacing1-w2-spacing1-w1
        t1=T+H-h1-spacing1

        self.firstButton=xbmcgui.ControlButton(l1,t1,w1,h1,firstButtonText,textColor="0xFF000000",focusedColor="0xFF000000",alignment=2,focusTexture=focus,noFocusTexture=nofocus)
        self.secondButton=xbmcgui.ControlButton(l2,t2,w2,h2,secondButtonText,textColor="0xFF000000",focusedColor="0xFF000000",alignment=2,focusTexture=focus,noFocusTexture=nofocus)

        for z in [self.BG,self.ImgMessage,self.TxtMessage,self.iLogo,self.secondButton,self.firstButton]:
            self.addControl(z)

        for z in [self.BG,self.ImgMessage,self.TxtMessage,self.iLogo,self.secondButton,self.firstButton]:
            z.setAnimations([('WindowOpen','effect=fade delay=0 time=1000 start=0 end=100'),('WindowClose','effect=slide delay=0 time=1000 start=0 end=0,'+str(0-(H+T+10)))])

        self.secondButton.controlLeft(self.firstButton)
        self.secondButton.controlRight(self.firstButton)
        self.firstButton.controlLeft(self.secondButton)
        self.firstButton.controlRight(self.secondButton)

        self.TxtMessage.setText(self.noteMessage)
        self.TxtMessage.autoScroll(20000, 2500, 15000) #all in ms -> delay, scroll speed (less is faster), repeat time
        self.setFocus(self.secondButton)


    def doFirstButtonAction(self):
        self.CloseWindow1st()

    def doSecondButtonAction(self):
        self.CloseWindow1st()

    def doDismiss(self):
        self.CloseWindow1st()

    def onAction(self,action):
        logger.debug("action launched: "+str(action))
        try:
            F=self.getFocus()
        except:
            F=False

        if action == ACTION_PREVIOUS_MENU:
            self.doFirstButtonAction()
        elif action == ACTION_NAV_BACK:
            self.doSecondButtonAction()
        elif action == ACTION_SELECT_ITEM:
            self.doDismiss()
        else:
            try:
                if not F==self.secondButton:
                    self.setFocus(self.firstButton)
            except:
                pass
    def onControl(self,control):
        if control==self.secondButton:
            self.doRemindMeLater()
        elif control== self.firstButton:
            self.doDismiss()
        else:
            try:
                self.setFocus(self.secondButton)
            except:
                pass
    #def onInit(self):
    #   pass
    #def onClick(self,control):
    #   pass
    #def onControl(self,control):
    #   pass
    #def onFocus(self,control):
    #   pass
    #def onAction(self,action):
    #   pass

    def CloseWindow1st(self):
        logger.debug("closing window...")
        self.close()
