from PyQt6.QtWidgets import QApplication, QStyleOptionButton, QStyleOptionViewItem, QStyledItemDelegate, QStyle
from PyQt6.QtCore import QEvent, Qt, QRect, QSize

class CustomDelegate(QStyledItemDelegate):
    CHECK_SIZE = 20
    CHECK_PADDING = 20
    TEXT_OFFSET = 50

    def _checkbox_rect(self, option_rect):
        return QRect(
            option_rect.left() + self.CHECK_PADDING,
            option_rect.top() + (option_rect.height() - self.CHECK_SIZE) // 2,
            self.CHECK_SIZE,
            self.CHECK_SIZE,
        )

    def editorEvent(self, event, model, option, index):
        if event.type() == QEvent.Type.MouseButtonRelease and \
            event.button() == Qt.MouseButton.LeftButton:
                if self._checkbox_rect(option.rect).contains(event.pos()):
                    current = index.data(Qt.ItemDataRole.CheckStateRole)
                    new_state = (
                        Qt.CheckState.Unchecked.value
                        if current == Qt.CheckState.Checked.value
                        else Qt.CheckState.Checked.value
                    )
                    model.setData(index, new_state, Qt.ItemDataRole.CheckStateRole)
                    return True
        return super().editorEvent(event, model, option, index)

    def paint(self, painter, option, index):
        if not index.isValid():
            return

        opt = QStyleOptionViewItem(option)
        opt.rect = option.rect.adjusted(0, 0, 0, 0)
        super().paint(painter, opt, index)

    def sizeHint(self, option, index):
        size = super().sizeHint(option, index)
        size.setHeight(60)
        return size