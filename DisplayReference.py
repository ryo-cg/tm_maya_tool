"""
RyoToyama
DisplayReference_v000
20250515
"""

from maya import cmds

# 変数の宣言
ovrEn = ".overrideEnabled"
ovrDis = ".overrideDisplayType"

# オブジェクトの取得
selected = cmds.ls(sl=True, long=True)

if not selected:
    cmds.warning("何も選択されていません。")
else:
    for obj in selected:
        cmds.setAttr(obj + ovrEn, 1.0)

        # DisplayTypeを設定（0=Normal, 1=Template, 2=Reference）
        cmds.setAttr(obj + ovrDis, 2.0)
