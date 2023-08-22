# coding:utf-8
import os
import sys
import time

import requests
from PyQt5 import uic
from PyQt5.QtCore import QUrl
from PyQt5.QtGui import QIcon, QDesktopServices, QImage
from PyQt5.QtWidgets import (QApplication, QFrame, QHBoxLayout, QLineEdit, QTableWidgetItem,
                             QTableView, QFileDialog)
from qfluentwidgets import (MessageBox, MSFluentWindow,
                            SubtitleLabel, setFont, TableWidget, PrimaryPushButton, StateToolTip, ImageLabel,
                            CommandBar, Action)
from qfluentwidgets import (setTheme, Theme, PrimaryToolButton,
                            ToolButton, LineEdit, ToolTipFilter, ToolTipPosition, ComboBox,
                            RadioButton)

from InfoBar import *
from Window.Variables import (ui_path, program_information)


def createFolders(folder_path):
    """
    创建文件夹
    :param folder_path:
    :return:
    """

    # 检查文件夹是否存在
    if not os.path.exists(folder_path):
        # 创建文件夹
        try:
            os.makedirs(folder_path)
            # print("文件夹已创建")
        except OSError as e:
            print(f"[!] 创建文件夹时出错: {e}")
            return str(e)
    else:
        # print("文件夹已存在")
        pass


class Widget(QFrame):

    def __init__(self, text: str, parent=None):
        super().__init__(parent=parent)
        self.label = SubtitleLabel(text, self)
        self.hBoxLayout = QHBoxLayout(self)

        setFont(self.label, 24)
        self.label.setAlignment(Qt.AlignCenter)
        self.hBoxLayout.addWidget(self.label, 1, Qt.AlignCenter)
        self.setObjectName(text.replace(' ', '-'))


class Window(MSFluentWindow):

    def __init__(self):
        super().__init__()
        self.ComboBoxItem = None
        self.FileChooseDialog = None
        self.DownloadPathButton = None
        self.DownloadPathInput = None
        self.DownloadButton = None
        self.program_language = 'zh-CN'

        # 新建子页面对象
        self.homeInterface = uic.loadUi(ui_path['Home'])
        self.settingInterface = uic.loadUi(ui_path['Setting'])

        # 初始化 Something...
        self.initNavigation()
        self.initWindow()
        self.initConnect()

        # 查找对象
        self.stateTooltip = None
        self.CookiesInput = self.homeInterface.findChild(LineEdit, "CookiesInput")
        self.UAInput = self.settingInterface.findChild(LineEdit, "UAInput")

    def CookiesSave(self):
        global UserCookies
        UserCookies = str(self.CookiesInput.text())
        if UserCookies in ('', ' '):
            print("[!] 为空，未输入 Cookies。")
            createErrorInfoBar(self, "错误！",
                               "你还没有输入 Cookies 呢！\n如何获取请点击帮助按钮。",
                               InfoBarPosition.BOTTOM, duration=-1
                               )
        else:
            print(f"[-] 获取到的用户 Cookies 为：{UserCookies}")
            createSuccessInfoBar(self, "成功！",
                                 "Cookies 已经录入！\n本程序不会记录你的 Cookies。"
                                 "\nCookies 仅在本次可以使用，\n下次启动将清空。",
                                 InfoBarPosition.BOTTOM_LEFT, 2000)
        print("[!] 已经保存 Cookies。")

    def UASave(self):
        global UserAgent
        UserAgent = str(self.UAInput.text())
        if UserAgent in ('', ' '):
            print("[!] 为空，未输入 UA。")
            createErrorInfoBar(self, "错误！",
                               "你还没有输入 UA 呢！\n已经自动填入默认 UA。",
                               InfoBarPosition.BOTTOM, duration=-1
                               )
            self.UAInput.setText(str(DefaultUA))
            UserAgent = DefaultUA
        elif UserAgent == DefaultUA:
            print("[-] 默认 UA。")
            createSuccessInfoBar(self, "你没有改变 UA。",
                                 "UA 已经录入！",
                                 InfoBarPosition.BOTTOM_LEFT, 2000)
        else:
            print(f"[-] 获取到的用户 UA 为：{UserAgent}")
            createSuccessInfoBar(self, "成功！",
                                 "UA 已经录入！",
                                 InfoBarPosition.BOTTOM_LEFT, 2000)
        print("[!] 已经保存 UA。")

    def ResetUA(self):
        self.UAInput.setText(str(DefaultUA))
        createSuccessInfoBar(self, "重置成功！",
                             "已经重置 UA。", InfoBarPosition.BOTTOM_LEFT,
                             2000)
        global UserAgent
        UserAgent = str(self.UAInput.text())

    def doGet(self):
        self.UASave()
        self.CookiesSave()
        global UserCookies
        headers = {
            'User-Agent': UserAgent,
            'Cookie': UserCookies
        }
        resp = requests.get(ApiUrl, headers=headers)
        global respData
        respData = resp.json()
        emotePackageNum = len(respData["data"]["packages"])
        global emoteInfos
        emoteInfos = []
        items = ["0 - 请选择你想要下载的表情"]
        for i in range(emotePackageNum):
            emotePackageName = respData["data"]["packages"][i]["text"]
            emoteInPackageNum = len(respData["data"]["packages"][i]['emote'])
            emotePackage = [str(i + 1), emotePackageName, str(emoteInPackageNum) + '个']
            item = f"{str(i + 1)} - 《{emotePackageName}》 - 共{str(emoteInPackageNum)}个表情"
            emoteInfos.append(emotePackage)
            items.append(item)
        # print(emoteInfos)

        TableView = self.homeInterface.findChild(TableWidget, "TableView")
        self.ComboBoxItem = self.homeInterface.findChild(ComboBox, "ComboBox")
        self.DownloadButton = self.homeInterface.findChild(PrimaryPushButton, "DownloadButton")
        self.DownloadButton.setIcon(FluentIcon.DOWN)

        TableView.setWordWrap(False)
        TableView.setRowCount(len(emoteInfos))
        TableView.setColumnCount(len(emoteInfos[0]))

        for i, emoteInfo in enumerate(emoteInfos):
            for j in range(len(emoteInfos[0])):
                TableView.setItem(i, j, QTableWidgetItem(emoteInfo[j]))

        TableView.verticalHeader().hide()
        TableView.setHorizontalHeaderLabels(['序号', '名字', '表情数量'])
        TableView.setEditTriggers(QTableView.NoEditTriggers)
        TableView.resizeColumnsToContents()
        # TableView.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        TableView.setColumnWidth(0, 55)
        TableView.setColumnWidth(1, 300)
        TableView.setColumnWidth(2, 90)

        self.ComboBoxItem.addItems(items)
        self.ComboBoxItem.setCurrentIndex(0)

        self.DownloadButton.clicked.connect(self.downloadEmote)

    def doDownload(self, index: int):
        if not DownloadPath == '':
            path = DownloadPath + f"/{respData['data']['packages'][index - 1]['text']}"
            createFolders(DownloadPath + f"/{respData['data']['packages'][index - 1]['text']}")
        else:
            path = f"{os.getenv('HomeDrive')}/Users/{os.getenv('UserName')}/Desktop/表情包/{respData['data']['packages'][index - 1]['text']}"
        createFolders(path)
        for item in respData['data']['packages'][index - 1]['emote']:
            emote_title = item['text'].strip('[').rstrip(']')
            emote = requests.get(item['url'])
            with open(rf'{path}\{emote_title}.png', 'wb') as f:
                f.write(emote.content)
                print('[!]', emote_title, '下载成功！')
        self.stopProgress()

    def downloadEmote(self):
        def call():
            self.DownloadButton.clicked.connect(call)

        def runProgress():
            if self.stateTooltip:
                # self.stateTooltip.setContent('下载完成啦 😆')
                # self.stateTooltip.setState(True)
                # self.stateTooltip = None
                pass
            else:
                self.stateTooltip = StateToolTip('正在下载', '请耐心等待哦~', self)
                self.stateTooltip.move(310, 65)
                self.stateTooltip.show()

        choiceIndex = self.ComboBoxItem.currentIndex()
        if not choiceIndex == 0:
            runProgress()
            self.doDownload(choiceIndex)
            global choicedIndex
            choicedIndex = choiceIndex
            self.DownloadButton.clicked.connect(call)

    def acceptDownloadPath(self):
        global DownloadPath
        DownloadPath = str(self.DownloadPathInput.text())
        e = createFolders(DownloadPath)
        if e:
            DownloadPath = ''
            title = '<h1>:(</h1>  出错啦！'
            content = f'创建文件夹失败！\n已经将自定义路径重设为默认。\n文本框并不会清除，请重新输入。\n\n具体错误：\n{str(e)}'
            Dialog = MessageBox(title, content, self)
            Dialog.yesButton.setText('是')
            Dialog.cancelButton.setText('否')

            if Dialog.exec():
                pass
                # QDesktopServices.openUrl(QUrl("https://afdian.net/a/zhiyiYo"))

        RadioButton_1 = self.settingInterface.findChild(RadioButton, "RadioButton")
        RadioButton_2 = self.settingInterface.findChild(RadioButton, "RadioButton_2")
        RadioButton_2.setChecked(True)
        RadioButton_1.setChecked(False)

    def stopProgress(self):
        if self.stateTooltip:
            self.stateTooltip.setContent('下载完成啦 😆')
            self.stateTooltip.setState(True)
            self.stateTooltip = None

    def initNavigation(self):
        # 添加子页面到边栏，注意顺序
        self.addSubInterface(self.homeInterface, FluentIcon.HOME,
                             program_information['menu_text']['Home'],
                             FluentIcon.HOME_FILL)
        self.addSubInterface(self.settingInterface, FluentIcon.SETTING,
                             program_information['menu_text']['Setting'],
                             FluentIcon.SETTING)

        self.navigationInterface.setCurrentItem(self.homeInterface.objectName())
        print("[*] 导航初始化完成！")

    def initWindow(self):
        # self.resize(500, 400)
        self.setWindowIcon(QIcon('bilibili.ico'))
        self.setWindowTitle(program_information['name'])

        desktop = QApplication.desktop().availableGeometry()
        width, height = desktop.width(), desktop.height()
        self.move(width // 2 - self.width() // 2, height // 2 - self.height() // 2)

        # 设置窗口固定尺寸
        self.setFixedSize(580, 430)
        UAInput = self.settingInterface.findChild(LineEdit, "UAInput")
        UAInput.setText(str(DefaultUA))
        shareBar = self.settingInterface.findChild(CommandBar, "CommandBar")
        IconLabel = self.settingInterface.findChild(ImageLabel, "ImageLabel")
        IconLabel.setPixmap(QImage("bilibili.png"))
        def shareApp():
            self.clipboard = QApplication.clipboard()
            self.AppUrl = "https://github.com/LimeBow-Studios/Bilibili-Emoji-Getter"
            self.clipboard.setText(str(self.AppUrl))
            createSuccessInfoBar(self, "复制成功！",
                                 "已经复制到剪贴板。",
                                 position=InfoBarPosition.TOP_RIGHT,
                                 duration=2000)
            title = f"你想要在浏览器中打开链接吗？"
            content = ("若你想打开链接，请点击「是」按钮；"
                       "\n若你想回到程序页面，请点击「否」按钮。"
                       "\n已经复制到剪切板。")
            # exitDialog = MessageDialog(title, content, self)   # Win10 style message box
            shareDialog = MessageBox(title, content, self)
            shareDialog.yesButton.setText('是')
            shareDialog.cancelButton.setText('否')
            if shareDialog.exec():
                QDesktopServices.openUrl(QUrl(self.AppUrl))
            else:
                pass

        shareBar.addAction(Action(FluentIcon.SHARE, '分享本程序', triggered=shareApp))

        print("[*] 窗口初始化成功！")

    def openFileChooseDialog(self):
        FolderDialog = QFileDialog.getExistingDirectory(self, "选择文件夹")
        self.DownloadPathInput.setText(str(FolderDialog))

    def initConnect(self):
        # print(f"[-] 当前语言：{program_information['lang']} ({self.program_language})。")
        # 查找对象
        CookiesInput = self.homeInterface.findChild(LineEdit, "CookiesInput")
        CookiesButton = self.homeInterface.findChild(PrimaryToolButton, "CookiesButton")
        CookiesHelpButton = self.homeInterface.findChild(ToolButton, "CookiesHelpButton")
        UAInput = self.settingInterface.findChild(LineEdit, "UAInput")
        UAButton = self.settingInterface.findChild(PrimaryToolButton, "UAButton")
        UAHelpButton = self.settingInterface.findChild(ToolButton, "UAHelpButton")
        DoIt = self.homeInterface.findChild(PushButton, 'DoIt')
        self.DownloadPathInput = self.settingInterface.findChild(LineEdit, "DownloadPathInput")
        self.DownloadPathButton = self.settingInterface.findChild(PrimaryToolButton, "DownloadPathButton")
        self.FileChooseDialog = self.settingInterface.findChild(ToolButton, "FileChooseDialog")

        # 定义槽函数
        def CookiesHelpMessageBox():
            title_CloseDialog = "Cookies 获取帮助"
            content_CloseDialog = ("要获取「Cookies 获取」相关的帮助内容，请点击「打开帮助网站」按钮。"
                                   "\n点击「取消」按钮会回到程序。")
            button1_CloseDialog = "打开帮助网站"
            button2_CloseDialog = "取消"
            CookiesGetHelpUrl = "https://github.com/LimeBow-Studios/Bilibili-Emoji-Getter/blob/main/Help/Cookie.md"
            exitDialog = MessageBox(title_CloseDialog, content_CloseDialog, self)
            exitDialog.yesButton.setText(button1_CloseDialog)
            exitDialog.cancelButton.setText(button2_CloseDialog)
            if exitDialog.exec():
                QDesktopServices.openUrl(QUrl(CookiesGetHelpUrl))

        # 组件设置
        CookiesInput.setEchoMode(QLineEdit.Password)
        CookiesInput.setClearButtonEnabled(True)
        CookiesInput.setToolTip("本程序不会记录你的 Cookies。"
                                "\nCookies 仅在本次可以使用，\n下次启动将清空。")
        CookiesInput.installEventFilter(
            ToolTipFilter(CookiesInput, 75, ToolTipPosition.BOTTOM)
        )
        CookiesButton.setToolTip("提交 Cookies")
        CookiesButton.installEventFilter(
            ToolTipFilter(CookiesButton, 75, ToolTipPosition.BOTTOM)
        )
        CookiesHelpButton.setToolTip("Cookies 帮助")
        CookiesHelpButton.installEventFilter(
            ToolTipFilter(CookiesHelpButton, 75, ToolTipPosition.BOTTOM)
        )
        CookiesButton.setIcon(FluentIcon.ACCEPT)
        CookiesHelpButton.setIcon(FluentIcon.QUESTION)

        UAInput.setClearButtonEnabled(True)
        UAInput.setToolTip("请填写UA")
        UAInput.installEventFilter(
            ToolTipFilter(UAInput, 75, ToolTipPosition.BOTTOM)
        )
        UAButton.setToolTip("提交 UA")
        UAButton.installEventFilter(
            ToolTipFilter(UAButton, 75, ToolTipPosition.BOTTOM)
        )
        UAHelpButton.setToolTip("重置 UA")
        UAHelpButton.installEventFilter(
            ToolTipFilter(UAHelpButton, 75, ToolTipPosition.BOTTOM)
        )
        UAButton.setIcon(FluentIcon.ACCEPT)
        UAHelpButton.setIcon(FluentIcon.CANCEL)
        DoIt.setIcon(FluentIcon.ADD)

        self.DownloadPathInput.setClearButtonEnabled(True)
        self.DownloadPathInput.setToolTip("请填写自定义路径")
        self.DownloadPathInput.installEventFilter(
            ToolTipFilter(self.DownloadPathInput, 75, ToolTipPosition.BOTTOM)
        )
        self.DownloadPathButton.setToolTip("提交路径")
        self.DownloadPathButton.installEventFilter(
            ToolTipFilter(self.DownloadPathButton, 75, ToolTipPosition.BOTTOM)
        )
        self.DownloadPathButton.setIcon(FluentIcon.ACCEPT)
        self.FileChooseDialog.setIcon(FluentIcon.FOLDER_ADD)

        # 连接槽函数
        CookiesInput.returnPressed.connect(self.CookiesSave)
        CookiesButton.clicked.connect(self.CookiesSave)
        UAInput.returnPressed.connect(self.UASave)
        UAButton.clicked.connect(self.UASave)
        CookiesHelpButton.clicked.connect(CookiesHelpMessageBox)
        UAHelpButton.clicked.connect(self.ResetUA)
        DoIt.clicked.connect(self.doGet)
        self.DownloadPathInput.returnPressed.connect(lambda: self.acceptDownloadPath())
        self.DownloadPathButton.clicked.connect(lambda: self.acceptDownloadPath())
        self.FileChooseDialog.clicked.connect(self.openFileChooseDialog)

        print("[*] 函数连接成功！")

    def closeEvent(self, event):
        def clearProgramCache():
            print("[!] 缓存已经清理。")

        def showCloseDialog():
            title_CloseDialog = f"你想要退出 {program_information['name']} 吗？"
            content_CloseDialog = ("若你想退出本程序，请点击「是」按钮；"
                                   "\n若你想回到程序页面，请点击「否」按钮。")
            # exitDialog = MessageDialog(title, content, self)   # Win10 style message box
            exitDialog = MessageBox(title_CloseDialog, content_CloseDialog, self)
            exitDialog.yesButton.setText('是')
            exitDialog.cancelButton.setText('否')
            if exitDialog.exec():
                print('[!] 用户确认退出。')
                clearProgramCache()
                self.setWindowOpacity(1)
                self.repaint()
                fadedOut()
            else:
                print('[?] 用户取消退出。')
                event.ignore()

        def fadedOut():
            for i in range(100, 0, -1):
                opacity = i / 100
                self.setWindowOpacity(opacity)
                self.repaint()
                time.sleep(0.0001)

            event.accept()

        showCloseDialog()


if __name__ == '__main__':
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)

    DownloadPath = ""
    choicedIndex = 0
    emoteInfos = []
    respData = {}
    ApiUrl = 'https://api.bilibili.com/x/emote/user/panel/web?business=reply'
    UserCookies = ""
    DefaultUA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36 Edg/97.0.1072.55'
    UserAgent = DefaultUA

    themeColor = 'Light'

    if themeColor == 'Light':
        setTheme(Theme.LIGHT)
    elif themeColor == 'Dark':
        setTheme(Theme.DARK)
    elif themeColor == 'Auto':
        setTheme(Theme.AUTO)
    else:
        setTheme(Theme.AUTO)

    app = QApplication(sys.argv)
    w = Window()
    w.show()
    print('[!] 程序已启动！')
    app.exec_()
