"""
20250530_v001
RyoToyama
AutoMakeAuxjnt
AuxJB
"""

from maya import OpenMayaUI, cmds
from PySide2 import QtWidgets
from shiboken2 import wrapInstance

# 定数変数
attrtf_ls = ["translate", "rotate", "scale"]
attrpb_ls = ["inRotate1", "rotInterpolation", "outRotate", "weight"]
xyz_ls = ["X", "Y", "Z"]
t_bind = "_jnt"
t_aux = "_auxjnt"
t_half = "_halfjnt"
t_pb = "_pb"
type_pb = "pairBlend"
type_jnt = "joint"
WINDOWNAME = "AuxTool"


def GetMayaWindow():
    ptr = OpenMayaUI.MQtUtil.mainWindow()
    return wrapInstance(int(ptr), QtWidgets.QMainWindow)


def ExecuteWindow():
    for widget in QtWidgets.QApplication.topLevelWidgets():
        if widget.objectName() == WINDOWNAME:
            widget.close()
            widget.deleteLater()


class AuxToolWindow(QtWidgets.QDialog):
    def __init__(self, parent=GetMayaWindow()):
        super(AuxToolWindow, self).__init__(parent)
        self.setWindowTitle(WINDOWNAME)
        self.Layout()

    def Layout(self):
        self.mainlayout = QtWidgets.QVBoxLayout(self)
        self.label = QtWidgets.QLabel()
        self.label.setText("補助骨の数")
        self.spinBox = QtWidgets.QSpinBox()
        self.spinBox.setMinimum(1)
        self.spinBox.setRange(1, 26)

        self.checkboxes = {}
        self.chboxlayout = QtWidgets.QHBoxLayout()
        for axis in xyz_ls:
            checkbox = QtWidgets.QCheckBox(axis)
            checkbox.setChecked(True)
            self.checkboxes[axis] = checkbox
            self.chboxlayout.addWidget(checkbox)

        self.mainlayout.addWidget(self.label)
        self.mainlayout.addWidget(self.spinBox)
        self.mainlayout.addLayout(self.chboxlayout)

        self.runbutton = QtWidgets.QPushButton("選択したツールを実行", self)
        self.runbutton.clicked.connect(self.Run)
        self.mainlayout.addWidget(self.runbutton)

    def Run(self):
        sljnt = cmds.ls(sl=True, type=type_jnt)
        auxval = self.spinBox.value()
        cmds.undoInfo(openChunk=True)  # アンドゥチャンクの開始
        try:
            for bjnt in sljnt:
                # バインド用ジョイントのみ通す
                if t_bind not in bjnt:
                    continue

                # 補助骨を作る
                halfjnt = self.Half(bjnt)
                print(f"HalfJoint: {halfjnt}")
                for val in range(auxval):
                    auxjnt = self.Aux(halfjnt, val)
                    print(f"Auxjoint: {auxjnt}, {val + 1}/{auxval}")
                pbnode = self.Cnct(bjnt, halfjnt)
                print(f"pairBlend: {pbnode}")

        finally:
            cmds.undoInfo(closeChunk=True)  # アンドゥチャンクの終了
            # cmds.select(sljnt, replace=True)

    def Half(self, bjnt):
        # ハーフ骨を作る
        halfname = bjnt.replace(t_bind, t_half)
        dupjnt = cmds.duplicate(bjnt, n=halfname, po=True)
        return dupjnt[0]

    def Aux(self, halfjnt, val):
        # 数をアルファベットに
        abc = chr(ord("A") + val)

        # 補助骨を作る
        auxname = halfjnt.replace(t_half, abc + t_aux)
        dupjnt = cmds.duplicate(halfjnt, n=auxname, po=True)
        cmds.parent(dupjnt[0], halfjnt)
        return dupjnt[0]

    def Cnct(self, bjnt, halfjnt):
        # pairBlendを作ってコネクトする
        slxyz = [axis for axis, cb in self.checkboxes.items() if cb.isChecked()]
        pbname = bjnt.replace(t_bind, t_pb)
        pb = cmds.createNode(type_pb, n=pbname)
        cmds.connectAttr(f"{bjnt}.{attrtf_ls[1]}", f"{pb}.{attrpb_ls[0]}", f=True)
        for xyz in slxyz:
            cmds.connectAttr(
                f"{pb}.{attrpb_ls[2]}{xyz}", f"{halfjnt}.{attrtf_ls[1]}{xyz}", f=True
            )
        cmds.setAttr(f"{pb}.{attrpb_ls[3]}", 0.5)
        cmds.setAttr(f"{pb}.{attrpb_ls[1]}", 1.0)


def main():
    ExecuteWindow()
    window = AuxToolWindow()
    window.setObjectName(WINDOWNAME)  # 名前を与え、それを判別する
    window.show()


main()
