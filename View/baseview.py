from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtWidgets import QHBoxLayout, QLabel, QPushButton


class BaseView:
    def __init__(self, parent_layout, renderinput, renderinput2):
        """初始化 BaseView，負責 UI 佈局與檔案選擇功能"""
        self.parent_layout = parent_layout  # 父布局
        self.render_input = renderinput  # 第一個渲染輸入
        self.render_input2 = renderinput2  # 第二個渲染輸入

    def choose_file(self, line_edit, file_filter):
        """選擇單個檔案，並將其路徑顯示在 line_edit 中"""
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(None, "選擇檔案", "", file_filter, options=options)
        if file_path:
            line_edit.setText(file_path)  # 設定選擇的檔案路徑
        else:
            line_edit.setText("")  # 若未選擇檔案，清空 line_edit
        return file_path

    def choose_image(self, line_edit):
        """選擇圖片檔案（僅限 PNG、JPG、JPEG），並將其路徑顯示在 line_edit 中"""
        options = QFileDialog.Options()
        file_filter = " Image (*.png *.jpg *.jpeg)"  # 設定圖片篩選條件
        file_path, _ = QFileDialog.getOpenFileName(None, "選擇檔案", "", file_filter, options=options)
        if file_path:
            line_edit.setText(file_path)  # 設定選擇的圖片路徑
        else:
            line_edit.setText(None)  # 若未選擇圖片，清空 line_edit
        return file_path

    def update_angle(self):
        """更新模型旋轉角度"""
        try:
            angle = float(self.angle_input.text())  # 從輸入框讀取旋轉角度
            self.model.set_model_angle(angle)  # 設定模型旋轉角度
        except ValueError:
            print("Invalid angle input")  # 若輸入無效，則輸出錯誤訊息

    def choose_folder(self, line_edit, set_model_callback):
        """選擇文件夾，並將其路徑傳遞給回呼函式（callback），顯示於 line_edit"""
        folder_path = QFileDialog.getExistingDirectory(None, "選擇文件夾")
        if folder_path:
            set_model_callback(folder_path)  # 更新模型的文件夾路徑
            line_edit.setText(folder_path)  # 顯示選擇的文件夾路徑
            return folder_path
        else:
            set_model_callback(folder_path)
            line_edit.setText(None)  # 若未選擇文件夾，清空 line_edit
            return None

    def create_file_selection_layout(self, parent_layout, label_text, line_edit, set_model):
        """創建通用文件夾選擇佈局，包含標籤、輸入框與選擇按鈕"""
        file_layout = QHBoxLayout()
        file_layout.addWidget(QLabel(label_text))  # 添加標籤
        file_layout.addWidget(line_edit)  # 添加輸入框
        button = QPushButton("選擇")  # 添加選擇按鈕
        button.clicked.connect(lambda: self.choose_folder(line_edit, set_model))  # 綁定選擇文件夾功能
        file_layout.addWidget(button)  # 將按鈕加入佈局
        parent_layout.addLayout(file_layout)  # 將文件選擇佈局添加至主佈局
