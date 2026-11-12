from PyQt6.QtWidgets import QApplication, QStyleOptionButton, QStyledItemDelegate, QStyle
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

        painter.save()

        if option.state & QStyle.StateFlag.State_Selected:
            painter.fillRect(option.rect, option.palette.highlight())

        text = index.data(Qt.ItemDataRole.DisplayRole)
        check = index.data(Qt.ItemDataRole.CheckStateRole)

        rect = option.rect
        x = rect.left() + self.CHECK_PADDING
        cy = rect.top() + rect.height() // 2

        if check is not None:
            opt = QStyleOptionButton()
            opt.state = QStyle.StateFlag.State_Enabled
            if check == Qt.CheckState.Checked.value:
                opt.state |= QStyle.StateFlag.State_On
            elif check == Qt.CheckState.PartiallyChecked.value:
                opt.state |= QStyle.StateFlag.State_NoChange
            else:
                opt.state |= QStyle.StateFlag.State_Off

            opt.rect = QRect(
                x,
                cy - self.CHECK_SIZE // 2,
                self.CHECK_SIZE,
                self.CHECK_SIZE
            )
            style = option.widget.style() if option.widget else QApplication.style()
            style.drawPrimitive(
                QStyle.PrimitiveElement.PE_IndicatorCheckBox, opt, painter
            )
            x += self.CHECK_SIZE + 10

        painter.setPen(option.palette.text().color())
        text_rect = option.rect.adjusted(self.TEXT_OFFSET, 0,0,0)
        painter.drawText(text_rect, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, text)
        painter.restore()

    def sizeHint(self, option, index):
        size = super().sizeHint(option, index)
        size.setHeight(60)
        return size