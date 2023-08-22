# coding:utf-8
from PyQt5.QtCore import QPoint, Qt

from qfluentwidgets import InfoBarIcon, InfoBar, PushButton, FluentIcon, InfoBarPosition, \
    InfoBarManager


@InfoBarManager.register('Custom')
class CustomInfoBarManager(InfoBarManager):
    """ Custom info bar manager """

    def _pos(self, infoBar: InfoBar, parentSize=None):
        p = infoBar.parent()
        parentSize = parentSize or p.size()

        # the position of first info bar
        x = (parentSize.width() - infoBar.width()) // 2
        y = (parentSize.height() - infoBar.height()) // 2

        # get the position of current info bar
        index = self.infoBars[p].index(infoBar)
        for bar in self.infoBars[p][0:index]:
            y += (bar.height() + self.spacing)

        return QPoint(x, y)

    def _slideStartPos(self, infoBar: InfoBar):
        pos = self._pos(infoBar)
        return QPoint(pos.x(), pos.y() - 16)


def createInfoInfoBar(self, title: str, content: str, position: InfoBarPosition, duration: int = 2000):
    w = InfoBar(
        icon=InfoBarIcon.INFORMATION,
        title=title,
        content=content,
        orient=Qt.Vertical,  # vertical layout
        isClosable=True,
        position=position,
        duration=duration,
        parent=self
    )
    w.addWidget(PushButton('Action'))
    w.show()


def createSuccessInfoBar(self, title: str, content: str, position: InfoBarPosition, duration: int = 2000):
    # convenient class mothod
    InfoBar.success(
        title=title,
        content=content,
        orient=Qt.Horizontal,
        isClosable=True,
        position=position,
        # position='Custom',   # NOTE: use custom info bar manager
        duration=duration,
        parent=self
    )


def createWarningInfoBar(self, title: str, content: str, position: InfoBarPosition, duration: int = 2000):
    InfoBar.warning(
        title=title,
        content=content,
        orient=Qt.Horizontal,
        isClosable=False,  # disable close button
        position=position,
        duration=duration,
        parent=self
    )


def createErrorInfoBar(self, title: str, content: str, position: InfoBarPosition, duration: int = -1):
    InfoBar.error(
        title=title,
        content=content,
        orient=Qt.Horizontal,
        isClosable=True,
        position=position,
        duration=duration,  # won't disappear automatically
        parent=self
    )


def createCustomInfoBar(self, icon: FluentIcon,
                        title: str, content: str,
                        position: InfoBarPosition, duration: int = 2000,
                        color: [str, str] = ['white', '#202020']):
    light_color, dark_color = color[0], color[1]
    w = InfoBar.new(
        icon=icon,
        title=title,
        content=content,
        orient=Qt.Horizontal,
        isClosable=True,
        position=position,
        duration=duration,
        parent=self
    )
    w.setCustomBackgroundColor(light_color, dark_color)
