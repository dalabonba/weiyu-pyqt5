# aipredictview.py
from PyQt5.QtWidgets import QGroupBox, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton
from .baseview import BaseView  
from PyQt5.QtWidgets import QFileDialog
import vtk

class ICPView(BaseView):
    def __init__(self, parent_layout, model,render_widget, renderinput,renderinput2):
        super().__init__(parent_layout, renderinput,renderinput2)
        self.model = model
        self.render_widget = render_widget
        self.interactor = self.render_widget.GetRenderWindow().GetInteractor()
        model.model_updated.connect(self.update_view)
        self.area_picker = vtk.vtkAreaPicker()
        self.render_widget.SetPicker(self.area_picker)




    def create_predict(self,parent_layout,current_panel):
        if current_panel:
            parent_layout.removeWidget(current_panel)

        panel = QGroupBox("ICP定位")
        layout = QVBoxLayout()

        front_layout, self.threefront_file = self.create_file_selector(
        "咬合面3D模型:", panel, "3D Model Files (*.ply *.stl *.obj)","front"
        )
        layout.addLayout(front_layout)

        left_layout, self.threeleft_file = self.create_file_selector(
        "左側3D模型:", panel, "3D Model Files (*.ply *.stl *.obj)","left"
        )

        right_layout, self.threeright_file = self.create_file_selector(
        "右側3D模型:", panel, "3D Model Files (*.ply *.stl *.obj)","right"
        )
        layout.addLayout(front_layout)
        layout.addLayout(left_layout)
        layout.addLayout(right_layout)


        # 輸出深度圖文件夾選擇
        self.output_folder = QLineEdit()
        self.create_file_selection_layout(layout, "輸出文件夾:", self.output_folder,self.model.set_output_folder)

        # 保存按鈕
        save_button = QPushButton("ICP定位")
        save_button.clicked.connect(self.save_icp_file) 
        layout.addWidget(save_button)

        panel.setLayout(layout)
        parent_layout.addWidget(panel)
        return panel


    def save_icp_file(self):
        if self.model.save_icp_file(self.render_input,self.render_input2):
            print("ICP successfully")
        else:
            print("Failed to save ICP")

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
        self.threefront_file.setText(self.model.front_file)
        self.threeleft_file.setText(self.model.left_file)
        self.threeright_file.setText(self.model.right_file)
        self.output_folder.setText(self.model.output_folder)
        self.model.render_model_icp(self.render_input)
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
            if  hasattr(self.model, 'front_file') and self.model.front_file:
                self.render_input.RemoveActor(self.model.front_actor)
                self.render_input.ResetCamera()
                self.render_input.GetRenderWindow().Render()
                self.model.front_file = ""
            elif  hasattr(self.model, 'left_file') and self.model.left_file:
                self.render_input.RemoveActor(self.model.left_actor)
                self.render_input.ResetCamera()
                self.render_input.GetRenderWindow().Render()
                self.model.left_file = ""
            elif  hasattr(self.model, 'right_file') and self.model.right_file:
                self.render_input.RemoveActor(self.model.right_actor)
                self.render_input.ResetCamera()
                self.render_input.GetRenderWindow().Render()
                self.model.right_file = ""
        self.update_view()
        return file_path