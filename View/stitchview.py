from PyQt5.QtWidgets import QGroupBox, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton
from .baseview import BaseView  
from Otherfunction import readmodel

class StitchView(BaseView):
    def __init__(self, parent_layout, model, renderinput, renderinput2):
        super().__init__(parent_layout, renderinput, renderinput2)
        self.model = model
        self.model.model_updated.connect(self.update_view)  # 連接到模型的更新信號，與 SingleDepthView 一致

    def create_stitch(self, parent_layout, current_panel):
        if current_panel:
            parent_layout.removeWidget(current_panel)

        panel = QGroupBox("縫合模型")
        layout = QVBoxLayout()

        # 缺陷模型檔案選擇
        prepare_layout = QHBoxLayout()  # 創建水平佈局
        prepare_layout.addWidget(QLabel("缺陷模型:"))  # 添加標籤
        self.prepare_file = QLineEdit()  # 創建文本框
        prepare_layout.addWidget(self.prepare_file)  # 添加文本框到佈局
        prepare_button = QPushButton("選擇")  # 創建選擇按鈕
        prepare_button.clicked.connect(self.choose_prepare_file)  # 連接到選擇檔案方法
        prepare_layout.addWidget(prepare_button)  # 添加按鈕到佈局
        layout.addLayout(prepare_layout)  # 添加佈局到主佈局

        # AIsmooth 模型檔案選擇
        smooth_layout = QHBoxLayout()  # 創建水平佈局
        smooth_layout.addWidget(QLabel("AIsmooth模型:"))  # 添加標籤
        self.smooth_ai_file = QLineEdit()  # 創建文本框
        smooth_layout.addWidget(self.smooth_ai_file)  # 添加文本框到佈局
        smooth_button = QPushButton("選擇")  # 創建選擇按鈕
        smooth_button.clicked.connect(self.choose_smooth_ai_file)  # 連接到選擇檔案方法
        smooth_layout.addWidget(smooth_button)  # 添加按鈕到佈局
        layout.addLayout(smooth_layout)  # 添加佈局到主佈局

        # 輸出資料夾選擇
        self.output_layout = QHBoxLayout()  # 創建一個水平佈局用於輸出文件夾選擇
        self.output_folder = QLineEdit()  # 創建一個用於輸入輸出文件夾路徑的文本框
        self.create_file_selection_layout(layout, "輸出文件夾:", self.output_folder, self.model.set_output_folder)  # 調用方法創建文件選擇佈局

        # 保存按鈕
        save_button = QPushButton("保存縫合結果")
        save_button.clicked.connect(self.save_stitch_model) 
        layout.addWidget(save_button)

        panel.setLayout(layout)
        parent_layout.addWidget(panel)
        return panel

    def choose_prepare_file(self):
        file_path = self.choose_file(self.prepare_file, "3D Model Files (*.ply *.stl *.obj)")  # 使用與 SingleDepthView 相同的檔案格式
        if file_path and self.model.set_prepare_file(file_path):  # 假設模型有 set_prepare_file 方法
            self.model.render_model(self.render_input)  # 渲染模型
        else:
            # 若無效則移除缺陷模型
            if hasattr(self.model, 'prepare_actor') and self.model.prepare_actor:
                self.render_input.RemoveActor(self.model.prepare_actor)
                self.render_input.ResetCamera()
                self.render_input.GetRenderWindow().Render()
            self.model.prepare_file = ""
            self.prepare_file.setText("")  # 清空文本框

    def choose_smooth_ai_file(self):
        file_path = self.choose_file(self.smooth_ai_file, "3D Model Files (*.ply *.stl *.obj)")  # 使用與 SingleDepthView 相同的檔案格式
        if file_path and self.model.set_smooth_ai_file(file_path):  # 假設模型有 set_smooth_ai_file 方法
            self.model.render_model(self.render_input)  # 渲染模型
        else:
            # 若無效則移除 AIsmooth 模型
            if hasattr(self.model, 'smooth_ai_actor') and self.model.smooth_ai_actor:
                self.render_input.RemoveActor(self.model.smooth_ai_actor)
                self.render_input.ResetCamera()
                self.render_input.GetRenderWindow().Render()
            self.model.smooth_ai_file = ""
            self.smooth_ai_file.setText("")  # 清空文本框


    def update_view(self):
        # 更新 UI 以反映模型的當前狀態
        self.prepare_file.setText(self.model.prepare_file)
        self.smooth_ai_file.setText(self.model.smooth_ai_file)
        self.output_folder.setText(self.model.output_folder)

    def save_stitch_model(self):
        if self.model.save_stitch_button(self.render_input, self.render_input2):
            print("Stitch saved successfully")
        else:
            print("Failed to save depth map")