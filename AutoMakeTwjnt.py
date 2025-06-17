"""
20250530_v001
RyoToyama
AutoMakeTwjnt
TwsJB
"""

from maya import OpenMayaUI, cmds
from PySide2 import QtWidgets
from shiboken2 import wrapInstance

# 定数変数
attrtf_ls = ["translate", "rotate", "scale"]
attrpb_ls = ["inRotate1", "rotInterpolation", "outRotate", "weight"]
xyz_ls = ["X", "Y", "Z"]
pc_ls = ["select", "child"]
t_bind = "_jnt"
t_operate = "_mjnt"
t_tw = "_twjnt"
t_pb = "_pb"
type_pb = "pairBlend"
type_jnt = "joint"
WINDOWNAME = "TwistTool"


def GetMayaWindow():
    ptr = OpenMayaUI.MQtUtil.mainWindow()
    return wrapInstance(int(ptr), QtWidgets.QMainWindow)


def ExecuteWindow():
    for widget in QtWidgets.QApplication.topLevelWidgets():
        if widget.objectName() == WINDOWNAME:
            widget.close()
            widget.deleteLater()


class TwistToolWindow(QtWidgets.QDialog):
    def __init__(self, parent=GetMayaWindow()):
        super(TwistToolWindow, self).__init__(parent)
        self.setWindowTitle(WINDOWNAME)
        self.Layout()

    def Layout(self):
        self.mainlayout = QtWidgets.QVBoxLayout(self)
        self.spinBox = QtWidgets.QSpinBox()
        self.spinBox.setMinimum(1)
        self.spinBox.setRange(1, 26)
        self.label = QtWidgets.QLabel()
        self.label.setText("ツイストジョイントの数")

        # XYZどの軸か
        self.radioGroupA = QtWidgets.QButtonGroup(self)
        radioLayoutA = QtWidgets.QHBoxLayout()
        self.radioButtonsA = {}
        for axis in xyz_ls:
            radio = QtWidgets.QRadioButton(axis)
            self.radioButtonsA[axis] = radio
            self.radioGroupA.addButton(radio)
            radioLayoutA.addWidget(radio)
        self.radioButtonsA[xyz_ls[0]].setChecked(True)

        # 親か子か
        self.radioGroupB = QtWidgets.QButtonGroup(self)
        radioLayoutB = QtWidgets.QHBoxLayout()
        self.radioButtonsB = {}
        for label in pc_ls:
            radio = QtWidgets.QRadioButton(label)
            self.radioButtonsB[label] = radio
            self.radioGroupB.addButton(radio)
            radioLayoutB.addWidget(radio)
        self.radioButtonsB[pc_ls[0]].setChecked(True)

        # UIをウィンドウに乗せる
        self.mainlayout.addWidget(self.spinBox)
        self.mainlayout.addWidget(self.label)
        self.mainlayout.addLayout(radioLayoutA)
        self.mainlayout.addLayout(radioLayoutB)

        self.runbutton = QtWidgets.QPushButton("選択したツールを実行", self)
        self.runbutton.clicked.connect(self.Run)
        self.mainlayout.addWidget(self.runbutton)

    def Run(self):
        sljnt = cmds.ls(sl=True, type=type_jnt)
        twval = self.spinBox.value()
        cmds.undoInfo(openChunk=True)  # アンドゥチャンクの開始
        try:
            for bjnt in sljnt:
                # バインド用ジョイントのみ通す
                if t_bind not in bjnt:
                    continue

                ch = cmds.listRelatives(bjnt, c=True, type=type_jnt)
                chijnt = ch[0]
                for slxyz, button in self.radioButtonsA.items():
                    if button.isChecked():
                        xyz = slxyz
                        break

                for slpc, button in self.radioButtonsB.items():
                    if button.isChecked():
                        pc = slpc
                        break

                interval = 1.0 / (twval + 1.0)
                for ran in range(twval):
                    val = ran + 1
                    # ツイスト骨を作る
                    twjnt = self.Twist(bjnt, val)
                    cmds.parent(twjnt, bjnt)
                    print(f"Twjoint: {twjnt}, {val}/{twval}")

                    # ツイスト骨を配置
                    pos = self.Setpos(twjnt, chijnt, interval, val, xyz, pc)
                    print(f"Position: {twjnt}, {pos}")

                    # ペアブレンドとコネクト
                    weight = self.Cnct(bjnt, chijnt, twjnt, interval, val, xyz, pc)
                    print(f"weight: {weight}")

        finally:
            cmds.undoInfo(closeChunk=True)  # アンドゥチャンクの終了
            cmds.select(sljnt, replace=True)

    def Twist(self, bjnt, val):
        abc = chr(ord("A") + val - 1)
        twname = bjnt.replace(t_bind, abc + t_tw)
        dupjnt = cmds.duplicate(bjnt, n=twname, po=True)
        return dupjnt[0]

    def Setpos(self, twjnt, chijnt, interval, val, xyz, pc):
        far = cmds.getAttr(f"{chijnt}.{attrtf_ls[0]}{xyz}")  # 距離
        if pc in pc_ls[0]:
            pos = far * interval * val
        elif pc in pc_ls[1]:
            pos = far - (far * interval * val)
        cmds.setAttr(f"{twjnt}.{attrtf_ls[0]}{xyz}", pos)
        return pos

    def Cnct(self, bjnt, chijnt, twjnt, interval, val, xyz, pc):
        abc = chr(ord("A") + val - 1)
        weight = interval * val
        if pc == pc_ls[0]:
            src = bjnt
        elif pc == pc_ls[1]:
            src = chijnt
        pbname = src.replace(t_bind, abc + t_pb)
        pb = cmds.createNode(type_pb, n=pbname)
        cmds.connectAttr(f"{src}.{attrtf_ls[1]}", f"{pb}.{attrpb_ls[0]}", f=True)
        cmds.connectAttr(
            f"{pb}.{attrpb_ls[2]}{xyz}", f"{twjnt}.{attrtf_ls[1]}{xyz}", f=True
        )
        cmds.setAttr(f"{pb}.{attrpb_ls[3]}", weight)
        cmds.setAttr(f"{pb}.{attrpb_ls[1]}", 1.0)
        return weight


def main():
    ExecuteWindow()
    window = TwistToolWindow()
    window.setObjectName(WINDOWNAME)  # 名前を与え、それを判別する
    window.show()


main()
