from PyQt5.QtWidgets import (QMainWindow, QVBoxLayout, QHBoxLayout, QPushButton, QWidget, QSpacerItem, 
                             QSizePolicy)
from PyQt5.QtCore import Qt
from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
import vtkmodules.all as vtk
from . import singledepthview, mutipledepthview,mutipledepthview,aipredictview,edgeview,remeshview,occlusionview
from Model import Singledepthmodel,Mutipledepthmodel


class View(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('AI牙冠平台')
        self.setGeometry(400, 150, 1400, 800)

        self.setup_ui()
        self.setup_vtk()
        self.connect_signals()
        self.current_panel = None

    def setup_ui(self):
        self.centralWidget = QWidget()
        self.setCentralWidget(self.centralWidget)
        self.mainLayout = QHBoxLayout(self.centralWidget)

        self.setup_button_panel()
        self.setup_vtk_widgets()

    def setup_button_panel(self):
        self.buttonPanel = QVBoxLayout()
        self.buttonPanel.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

        self.buttons = {
            "depthButton": "單次創建深度圖",
            "mutiple_depthButton": "多次創建深度圖",
            "edgeButton": "獲得牙齒邊界線圖",
            "occlusionButton": "獲得咬合重疊處",
            "predictButton": "AI預測",
            "reconstructButton": "3D模型重建"
        }

        buttonStyle = "font-size: 26px; font-family: '標楷體', 'Times New Roman'; font-weight: bold;"

        for attr, text in self.buttons.items():
            button = QPushButton(text)
            button.setStyleSheet(buttonStyle)
            setattr(self, attr, button)
            self.buttonPanel.addWidget(button)
            self.buttonPanel.addSpacing(20)
        self.buttonPanel.addStretch(1)


        self.mainLayout.addLayout(self.buttonPanel, 1)

    def setup_vtk_widgets(self):
        self.vtkWidget1 = QVTKRenderWindowInteractor(self.centralWidget)
        self.vtkWidget2 = QVTKRenderWindowInteractor(self.centralWidget)

        self.mainLayout.addWidget(self.vtkWidget1, 4)
        self.mainLayout.addWidget(self.vtkWidget2, 4)

    def setup_vtk(self):
        # Setup for vtkWidget1
        self.vtk_renderer1 = vtk.vtkRenderer()
        self.vtkWidget1.GetRenderWindow().AddRenderer(self.vtk_renderer1)
        self.iren1 = self.vtkWidget1.GetRenderWindow().GetInteractor()
        self.vtk_renderer1.SetBackground(0.1, 0.2, 0.4)
        
        # Set the size of the widget to 256x256
        self.vtkWidget1.setFixedSize(768, 768)
        self.iren1.Initialize()

        # Setup for vtkWidget2
        self.vtk_renderer2 = vtk.vtkRenderer()
        self.vtkWidget2.GetRenderWindow().SetSharedRenderWindow(self.vtkWidget1.GetRenderWindow())
        self.vtkWidget2.GetRenderWindow().AddRenderer(self.vtk_renderer2)
        self.iren2 = self.vtkWidget2.GetRenderWindow().GetInteractor()
        self.vtk_renderer2.SetBackground(0.1, 0.4, 0.2)

        # Set the size of the widget to 256x256
        self.vtkWidget2.setFixedSize(768, 768)
        self.iren2.Initialize()


    def connect_signals(self):
        self.depthButton.clicked.connect(lambda: self.create_depth_panel())
        self.mutiple_depthButton.clicked.connect(lambda: self.create_multiple_depth_panel())
        self.edgeButton.clicked.connect(lambda: self.create_edge_panel())
        self.occlusionButton.clicked.connect(lambda: self.create_occlusion_panel())
        self.predictButton.clicked.connect(lambda: self.create_predict_panel())
        self.reconstructButton.clicked.connect(lambda: self.create_reconstruct_panel())



    def create_depth_panel(self):
        self.clear_renderers()    
        self.function_view = singledepthview.SingleDepthView(self.buttonPanel,Singledepthmodel.SingleDepthModel(),self.vtk_renderer1)
        self.current_panel = self.function_view.create_depth(self.buttonPanel,self.current_panel)

    def create_multiple_depth_panel(self):
        self.clear_renderers()    
        self.function_view = mutipledepthview.MutipleDepthView(self.buttonPanel,Mutipledepthmodel.BatchDepthModel(),self.vtk_renderer1)
        self.current_panel = self.function_view.create_depth(self.buttonPanel,self.current_panel)

    def create_edge_panel(self):
        self.clear_renderers()    
        self.function_view = edgeview.ImageedgeView(self.buttonPanel,Mutipledepthmodel.BatchDepthModel(),self.vtk_renderer1)
        self.current_panel = self.function_view.create_depth(self.buttonPanel,self.current_panel)

    def create_occlusion_panel(self):
        self.clear_renderers()    
        self.function_view = occlusionview.OcclusionView(self.buttonPanel,Mutipledepthmodel.BatchDepthModel(),self.vtk_renderer1)
        self.current_panel = self.function_view.create_depth(self.buttonPanel,self.current_panel)

    def create_predict_panel(self):
        # Create panel for AI prediction
        self.clear_renderers()    
        self.function_view = aipredictview.AimodelView(self.buttonPanel,Mutipledepthmodel.BatchDepthModel(),self.vtk_renderer1)
        self.current_panel = self.function_view.create_depth(self.buttonPanel,self.current_panel)

    def create_reconstruct_panel(self):
        self.clear_renderers()    
        self.function_view = remeshview.RemeshView(self.buttonPanel,Mutipledepthmodel.BatchDepthModel(),self.vtk_renderer1)
        self.current_panel = self.function_view.create_depth(self.buttonPanel,self.current_panel)


    def clear_renderers(self):
        self.vtk_renderer1.RemoveAllViewProps()  # Remove all actors and props from renderer1
        self.vtk_renderer2.RemoveAllViewProps()  # Remove all actors and props from renderer2
        
        self.vtk_renderer1.Render()  # Update the renderer1 to reflect the changes
        self.vtk_renderer2.Render()  # Update the renderer2 to reflect the changes

    def closeEvent(self, event):
        self.cleanup()
        event.accept()

    def cleanup(self):
        for iren in [self.iren1, self.iren2]:
            if iren:
                iren.GetRenderWindow().Finalize()
                iren.TerminateApp()

        for attr in ['vtkWidget1', 'vtkWidget2', 'vtk_renderer1', 'vtk_renderer2', 'iren1', 'iren2']:
            setattr(self, attr, None)