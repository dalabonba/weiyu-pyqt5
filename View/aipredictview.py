# aipredictview.py
from PyQt5.QtWidgets import QFrame,QGroupBox, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton
from .baseview import BaseView  
from PyQt5.QtWidgets import QFileDialog
import vtk
from forvtk import forvtkinteractor

class AimodelView(BaseView):
    def __init__(self, parent_layout, model,render_widget, renderinput,renderinput2):
        super().__init__(parent_layout, renderinput,renderinput2)
        self.model = model
        self.render_widget = render_widget
        self.interactor = self.render_widget.GetRenderWindow().GetInteractor()
        self.detect_redownmodel = False
        model.model_updated.connect(self.update_view)
        self.area_picker = vtk.vtkAreaPicker()
        self.render_widget.SetPicker(self.area_picker)
        self.highlight_style = forvtkinteractor.HighlightInteractorStyle()
        self.interactor.SetInteractorStyle(self.highlight_style)



    def create_predict(self,parent_layout,current_panel):
        if current_panel:
            parent_layout.removeWidget(current_panel)

        panel = QGroupBox("AI預測")
        layout = QVBoxLayout()

        lower_layout, self.threeddown_file = self.create_file_selector(
        "下顎缺陷3D模型:", panel, "3D Model Files (*.ply *.stl *.obj)","down"
        )
        layout.addLayout(lower_layout)

        upper_layout, self.threedupper_file = self.create_file_selector(
        "上顎3D模型:", panel, "3D Model Files (*.ply *.stl *.obj)","up"
        )
        layout.addLayout(lower_layout)
        layout.addLayout(upper_layout)


        self.model_file = QLineEdit()
        self.create_file_selection_layout(layout, "預訓練模型:", self.model_file,self.model.set_model_folder)


        # 輸出深度圖文件夾選擇
        self.output_folder = QLineEdit()
        self.create_file_selection_layout(layout, "輸出文件夾:", self.output_folder,self.model.set_output_folder)

        # 保存按鈕
        save_button = QPushButton("AI預測")
        save_button.clicked.connect(self.save_ai_file) 
        layout.addWidget(save_button)

        panel.setLayout(layout)
        parent_layout.addWidget(panel)
        return panel


    def save_ai_file(self):
        if self.model.save_ai_file(self.render_input,self.render_input2):
            print("Depth map saved successfully")
        else:
            print("Failed to save depth map")

    def create_file_selector(self,label_text, parent, file_types,position_type):
        layout = QHBoxLayout()
        label = QLabel(label_text)
        layout.addWidget(label)
        file_input = QLineEdit()
        layout.addWidget(file_input)
        button = QPushButton("選擇")
        button.clicked.connect(lambda: self.choose_file(file_input, file_types,position_type))
        layout.addWidget(button)
        return layout, file_input
    
    def update_view(self):
        self.render_input.RemoveAllViewProps()  # Clear all actors
        self.model_file.setText(self.model.model_folder)
        self.threeddown_file.setText(self.model.lower_file)
        self.threedupper_file.setText(self.model.upper_file)
        self.output_folder.setText(self.model.output_folder)
        self.model.render_model(self.render_input)
        if self.model.lower_file != '':
            self.highlight_style.SetPolyData(self.model.model2)
        self.render_input.ResetCamera()
        self.render_input.GetRenderWindow().Render()


    def choose_file(self, line_edit, file_filter,position_type):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(None, "選擇檔案", "", file_filter, options=options)
        if file_path:
            line_edit.setText(file_path)
            if hasattr(self, 'model'):
                if any(file_path.lower().endswith(ext) for ext in ['.ply', '.stl', '.obj']):
                    self.model.set_reference_file(file_path,position_type)
        else:
            if  hasattr(self.model, 'lower_actor') and self.model.lower_actor:
                self.render_input.RemoveActor(self.model.lower_actor)
                self.render_input.ResetCamera()
                self.render_input.GetRenderWindow().Render()
                self.model.lower_file = ""
                self.model.lower_center = None
                self.model.models_center = None
            elif hasattr(self.model, 'upper_actor') and self.model.upper_actor:
                self.render_input.RemoveActor(self.model.upper_actor)
                self.render_input.ResetCamera()
                self.render_input.GetRenderWindow().Render()
                self.model.upper_file = ""
                self.model.upper_center = None
                self.model.models_center = None
        self.update_view()
        return file_path