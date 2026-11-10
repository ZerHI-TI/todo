from PyQt6.QtWidgets import QStyledItemDelegate, QStyle
from PyQt6.QtCore import Qt, QRect, QSize

class CustomDelegate(QStyledItemDelegate):
    def paint(self, painter, option, index):
        if not index.isValid():
            return

        painter.save()

        if option.state & QStyle.StateFlag.State_Selected:
            painter.fillRect(option.rect, option.palette.highlight())

        text = index.data(Qt.ItemDataRole.DisplayRole)
        icon = index.data(Qt.ItemDataRole.DecorationRole)

        if icon:
            icon_rect = QRect(option.rect)
            icon_rect.setSize(QSize(40,40))
            icon.paint(painter, icon_rect, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        painter.setPen(option.palette.text().color())
        text_rect = option.rect.adjusted(60,0,0,0)
        painter.drawText(text_rect, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, text)
        painter.restore()

    def sizeHint(self, option, index):
        size = super().sizeHint(option, index)
        size.setHeight(60)
        return size