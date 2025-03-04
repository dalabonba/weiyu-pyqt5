# class HighlightInteractorStyle(vtk.vtkInteractorStyleRubberBandPick):
#     def __init__(self, parent=None):
#         self.AddObserver("LeftButtonReleaseEvent", self.OnLeftButtonUpEvent)
#         self.AddObserver("KeyPressEvent", self.OnKeyPress)
#         self.pickingEnabled = False
#         self.selectedCells = None  # To store selected cells for deletion

#         self.SelectedMapper = vtk.vtkCompositePolyDataMapper2()
#         self.SelectedActor = vtk.vtkActor()
#         self.SelectedActor.SetMapper(self.SelectedMapper)
#         self.SelectedActor.GetProperty().SetColor(1.0, 0.0, 0.0)  # Red

#     def OnKeyPress(self, obj, event):
#         key = self.GetInteractor().GetKeySym()
#         # Toggle pickingEnabled when 'r' is pressed
#         if key == 'r':
#             self.pickingEnabled = not self.pickingEnabled
#         # If 'Delete' key is pressed, delete the selected cells
#         elif key == 'Delete' and self.selectedCells and self.selectedCells.GetNumberOfCells() > 0:
#             self.DeleteSelectedCells()
#     def SetPolyData(self, polydata):
#         self.polydata = polydata

#     def OnLeftButtonUpEvent(self, obj, event):
#         if self.selectedCells is not None:
#             self.GetInteractor().GetRenderWindow().GetRenderers().GetFirstRenderer().RemoveActor(self.SelectedActor)
#             self.selectedCells = None
#         self.SelectedMapper = vtk.vtkCompositePolyDataMapper2()
#         self.SelectedActor = vtk.vtkActor()
#         self.SelectedActor.SetMapper(self.SelectedMapper)
#         self.SelectedActor.GetProperty().SetColor(1.0, 0.0, 0.0)  # Red
#         # self.GetInteractor().GetRenderWindow().Render()
#         self.OnLeftButtonUp()
#         if self.pickingEnabled:
#             frustum = self.GetInteractor().GetPicker().GetFrustum()

#             # 使用 vtkIdFilter 來保留原始索引
#             id_filter = vtk.vtkIdFilter()
#             id_filter.SetInputData(self.polydata)
#             id_filter.SetPointIds(False)
#             id_filter.SetCellIds(True)  # 保留 Cell IDs
#             id_filter.Update()

#             # 更新 extract 使用處理過的資料
#             self.extract = vtk.vtkExtractPolyDataGeometry()
#             self.extract.SetInputData(id_filter.GetOutput())
#             self.extract.SetImplicitFunction(frustum)
#             self.extract.Update()

#             # 取得篩選後的 PolyData
#             selected_polydata = self.extract.GetOutput()
#             selected_polydata.GetCellData().SetActiveScalars("vtkIdFilter_Ids")

#             # 儲存篩選出的單元
#             if selected_polydata.GetNumberOfCells() > 0:
#                 self.selectedCells = selected_polydata
#                 self.SelectedMapper.SetInputData(self.selectedCells)
#                 self.SelectedMapper.ScalarVisibilityOff()
#                 self.GetInteractor().GetRenderWindow().GetRenderers().GetFirstRenderer().AddActor(self.SelectedActor)
#                 self.GetInteractor().GetRenderWindow().Render()

#     def DeleteSelectedCells(self):
#         """
#         Delete the selected cells from the original polydata using original cell IDs safely.
#         """
#         if self.selectedCells is not None and self.selectedCells.GetNumberOfCells() > 0:
#             # 從選取的 PolyData 中取得原始索引
#             original_ids = [
#                 int(self.selectedCells.GetCellData().GetScalars().GetTuple(i)[0]) 
#                 for i in range(self.selectedCells.GetNumberOfCells())
#             ]

#             # 建立一個 mask 標記要刪除的單元
#             mask = vtk.vtkUnsignedCharArray()
#             mask.SetName("Mask")
#             mask.SetNumberOfComponents(1)
#             mask.SetNumberOfTuples(self.polydata.GetNumberOfCells())
#             mask.Fill(1)  # 預設為保留 (1)

#             # 將需要刪除的單元標記為 0
#             for cell_id in original_ids:
#                 mask.SetValue(cell_id, 0)

#             # 將 mask 加入到 polydata 中
#             self.polydata.GetCellData().AddArray(mask)
#             self.polydata.GetCellData().SetActiveScalars("Mask")

#             # 使用 vtkThreshold 過濾掉 Mask = 0 的單元 (刪除)
#             threshold = vtk.vtkThreshold()
#             threshold.SetInputData(self.polydata)
#             threshold.ThresholdBetween(1, 1)  # 只保留 Mask = 1 的單元
#             threshold.Update()

#             # 使用 vtkGeometryFilter 將結果轉換回 polydata 格式
#             geometry_filter = vtk.vtkGeometryFilter()
#             geometry_filter.SetInputData(threshold.GetOutput())
#             geometry_filter.Update()

#             # 將處理後的 polydata 設置回 self.polydata
#             self.polydata.DeepCopy(geometry_filter.GetOutput())
#             self.polydata.Modified()

#             self.SelectedMapper.SetInputData(self.polydata)
#             self.reactor = vtk.vtkActor()
#             self.reactor.SetMapper(self.SelectedMapper)
#             self.reactor.GetProperty().SetColor((0.0, 1.0, 0.0))
#             # self.SelectedMapper.ScalarVisibilityOff()  # 關閉標量可視化，使用單一顏色

#             # 移除選取的單元的可視化
#             self.GetInteractor().GetRenderWindow().GetRenderers().GetFirstRenderer().RemoveActor(self.SelectedActor)
#             self.GetInteractor().GetRenderWindow().GetRenderers().GetFirstRenderer().AddActor(self.reactor)
#             self.GetInteractor().GetRenderWindow().Render()


#             print(f"已成功刪除 {len(original_ids)} 個單元")



# import vtk
# class PointInteractor(vtk.vtkInteractorStyleTrackballCamera):
#     def __init__(self):
#         super().__init__()
#         # self.poly_data = poly_data
#         # self.dijkstra = vtk.vtkDijkstraGraphGeodesicPath()
#         # self.dijkstra.SetInputData(self.poly_data)
#         self.sphereActors = []
#         self.lineActors = []
#         self.pathList = []
#         self.loop = vtk.vtkImplicitSelectionLoop()

#         self.AddObserver("LeftButtonPressEvent", self.onLeftButtonDown)
#     def SetPolyData(self, polydata):
#         self.polydata = polydata
#         self.dijkstra = vtk.vtkDijkstraGraphGeodesicPath()
#         self.dijkstra.SetInputData(self.polydata)
#     # 滑鼠左鍵按下
#     def onLeftButtonDown(self,obj,event):
#         clickPos = self.GetInteractor().GetEventPosition()
#         picker = vtk.vtkCellPicker()
#         picker.Pick(clickPos[0],clickPos[1],0,self.GetInteractor().GetRenderWindow().GetRenderers().GetFirstRenderer())
#         if(picker.GetCellId() != -1):
#             # 視覺化選取點
#             self.pathList.append(picker.GetPointId())
#             point_position = self.polydata.GetPoint(picker.GetPointId())
#             sphereSource = vtk.vtkSphereSource()
#             sphereSource.SetCenter(point_position)
#             sphereSource.SetRadius(0.02)
#             sphereMapper = vtk.vtkPolyDataMapper()
#             sphereMapper.SetInputConnection(sphereSource.GetOutputPort())
#             self.sphereActor = vtk.vtkActor()
#             self.sphereActor.SetMapper(sphereMapper)
#             self.sphereActor.GetProperty().SetColor(1.0, 0.0, 0.0)
#             self.GetInteractor().GetRenderWindow().GetRenderers().GetFirstRenderer().AddActor(self.sphereActor)
#             self.sphereActors.append(self.sphereActor)
#             # 求最小路徑
#             if len(self.pathList) > 1:
#                 self.dijkstra.SetStartVertex(self.pathList[-2])
#                 self.dijkstra.SetEndVertex(self.pathList[-1])
#                 self.dijkstra.Update()

#                 idList = self.dijkstra.GetIdList()

#                 for i in range(idList.GetNumberOfIds() - 1):
#                     # 視覺化選取線
#                     id0 = idList.GetId(i)
#                     id1 = idList.GetId(i + 1)
                    
#                     self.line = vtk.vtkLineSource()
#                     self.line.SetPoint1(self.polydata.GetPoint(id0))
#                     self.line.SetPoint2(self.polydata.GetPoint(id1))
#                     lineMapper = vtk.vtkPolyDataMapper()
#                     lineMapper.SetInputConnection(self.line.GetOutputPort())
#                     self.lineActor = vtk.vtkActor()
#                     self.lineActor.SetMapper(lineMapper)
#                     self.lineActor.GetProperty().SetColor(1.0, 0.0, 0.0)
#                     self.GetInteractor().GetRenderWindow().GetRenderers().GetFirstRenderer().AddActor(self.lineActor)
#                     self.lineActors.append(self.lineActor)
#             self.GetInteractor().GetRenderWindow().Render()
#     # 封閉選取範圍
#     def closeArea(self):
#         if self.pathList[0] == self.pathList[-1]:
#             selectionPoints = vtk.vtkPoints()
#             selectionPoints.SetNumberOfPoints(len(self.pathList))
#             for i in range(len(self.pathList)):
#                 selectionPoints.SetPoint(i,self.polydata.GetPoint(self.pathList[i]))
#             self.loop.SetLoop(selectionPoints)
#             clip = vtk.vtkClipPolyData()
#             clip.SetInputData(self.polydata)
#             clip.SetClipFunction(self.loop)
#             clip.InsideOutOn()

#             clipMapper = vtk.vtkPolyDataMapper()
#             clipMapper.SetInputConnection(clip.GetOutputPort())

#             backProp = vtk.vtkProperty()
#             backProp.SetColor(1.0, 0.0, 0.0)

#             clipActor = vtk.vtkActor()
#             clipActor.SetMapper(clipMapper)
#             clipActor.SetProperty(backProp)

#             self.GetInteractor().GetRenderWindow().GetRenderers().GetFirstRenderer().AddActor(clipActor)
#             self.GetInteractor().GetRenderWindow().Render()

import vtk
from.Point import PointInteractor
from.Lasso import LassoInteractor

# 選取類別
class HighlightInteractorStyle(vtk.vtkInteractorStyleRubberBand3D):
    def __init__(self):
        super().__init__()
        
        # 選取模式開關
        self.boxSltMode = False 
        self.pointSltMode = False
        self.lassoSltMode = False
        
        self.start_position = None
        self.end_position = None
        self.geometry_filter = None
        self.selected_poly_data = None
        self.extract_geometry = None
        self.mapper = vtk.vtkPolyDataMapper()
        self.actor = vtk.vtkActor()
        self.boxArea = vtk.vtkAreaPicker()
        # 選取模式監聽器
        self.AddObserver("KeyPressEvent", self.modeSltKeyPress)
        self.AddObserver("LeftButtonReleaseEvent", self.onLeftButtonUp)
        self.AddObserver("LeftButtonPressEvent", self.onLeftButtonDown)
    def SetPolyData(self, polydata):
        self.polydata = polydata
        self.renderer = self.GetInteractor().GetRenderWindow().GetRenderers().GetFirstRenderer()
        self.point_func = PointInteractor(self.polydata)
        self.lasso_func = LassoInteractor(self.polydata)
    # 選取模式
    def modeSltKeyPress(self, obj, event):
        self.key = self.GetInteractor().GetKeySym()
        # 矩形選取模式
        if self.key == "c" or self.key == "C":
            if not self.boxSltMode:
                self.boxSltMode = True
            else:
                self.boxSltMode = False
        # 點選取模式
        elif self.key == "p" or self.key == "P":
            if not self.pointSltMode:
                self.point_func.pathList = []
                self.pointSltMode = True
            else:
                self.pointSltMode = False
                self.point_func.unRenderAllSelectors(self.renderer,self.GetInteractor())
        # 套索選取模式
        elif self.key == "l" or self.key == "L":
            if not self.lassoSltMode:
                self.lasso_func.pickpointId = []
                self.lassoSltMode = True
                self.boxSltMode = False
                self.pointSltMode = False
            else:
                self.lassoSltMode = False
        # 矩形刪除範圍
        elif self.key == "Delete"  and self.boxSltMode:
            self.removeCells(self.selection_frustum)
        # 點刪除範圍
        elif self.key == "Delete" and self.pointSltMode:
            self.removeCells(self.point_func.loop)
            self.point_func.unRenderAllSelectors(self.renderer,self.GetInteractor())
        # 套索刪除範圍
        elif self.key == "Delete" and self.lassoSltMode:
            self.removeCells(self.lasso_func.loop)
            self.lasso_func.unRenderAllSelectors(self.renderer,self.GetInteractor())
        # 封閉點選取範圍
        elif self.key == "Return":
            self.point_func.closeArea(self.GetInteractor(),self.renderer)
        # 取消上一步選取
        elif self.key == "BackSpace":
            self.point_func.cancelLastSelection(self.renderer,self.GetInteractor())
    # 移除選取範圍
    def removeCells(self,selection_frustum):
        if not isinstance(selection_frustum, vtk.vtkImplicitFunction):
            return

        clipper = vtk.vtkClipPolyData()
        clipper.SetInputData(self.polydata) 
        clipper.SetClipFunction(selection_frustum)
        clipper.GenerateClippedOutputOff()
        clipper.Update()

        new_poly_data = clipper.GetOutput()

        if new_poly_data.GetNumberOfCells() == 0:
            return

        self.polydata.DeepCopy(new_poly_data)
        self.renderer.RemoveActor(self.actor)

        self.mapper.SetInputData(self.polydata)
    
        self.GetInteractor().GetRenderWindow().Render()
    # 滑鼠左鍵按下
    def onLeftButtonDown(self,obj,event):
        if self.boxSltMode:
            self.start_position = self.GetInteractor().GetEventPosition()
            self.OnLeftButtonDown()
        elif self.pointSltMode:
            self.point_func.onLeftButtonDown(obj,event,self.GetInteractor(),self.renderer)
        elif self.lassoSltMode:
            self.lasso_func.onLeftButtonDown(obj,event,self.GetInteractor(),self.renderer)
    # 滑鼠左鍵放開
    def onLeftButtonUp(self,obj,event):
        if self.boxSltMode:
            self.end_position = self.GetInteractor().GetEventPosition()
            self.boxArea.AreaPick(self.start_position[0],self.start_position[1],self.end_position[0],self.end_position[1],self.renderer)
            self.selection_frustum = self.boxArea.GetFrustum()
            self.extract_geometry = vtk.vtkExtractGeometry()
            self.extract_geometry.SetInputData(self.polydata)
            self.extract_geometry.SetImplicitFunction(self.selection_frustum)
            self.extract_geometry.Update()
            self.selected_poly_data = self.extract_geometry.GetOutput()   
            self.geometry_filter = vtk.vtkGeometryFilter()
            self.geometry_filter.SetInputData(self.selected_poly_data)
            self.geometry_filter.Update()
            self.mapper.SetInputData(self.geometry_filter.GetOutput())
            self.actor.SetMapper(self.mapper)
            self.actor.GetProperty().SetColor(1.0, 0.0, 0.0) 
            self.renderer.AddActor(self.actor)
            self.OnLeftButtonUp()
            self.GetInteractor().GetRenderWindow().Render()