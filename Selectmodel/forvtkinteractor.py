import vtk
from .Point import PointInteractor
from .Lasso import LassoInteractor

class HighlightInteractorStyle(vtk.vtkInteractorStyleRubberBand3D):
    def __init__(self):
        super().__init__()
        # 選取模式開關
        self.boxSltMode = False
        self.pointSltMode = False
        self.lassoSltMode = False
        self.throughBtnMode = False  # 新增穿透模式

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

    def modeSltKeyPress(self, obj, event):
        self.key = self.GetInteractor().GetKeySym()
        interactor = self.GetInteractor()
        renderer = self.renderer

        # 矩形選取模式
        if self.key in ["c", "C"]:
            self.boxSltMode = not self.boxSltMode
            self.pointSltMode = False
            self.lassoSltMode = False
        # 點選取模式
        elif self.key in ["p", "P"]:
            if not self.pointSltMode:
                self.pointSltMode = True
                self.boxSltMode = False
                self.lassoSltMode = False
                self.point_func = PointInteractor(self.polydata)
            else:
                self.pointSltMode = False
        # 套索選取模式
        elif self.key in ["l", "L"]:
            if not self.lassoSltMode:
                self.lassoSltMode = True
                self.boxSltMode = False
                self.pointSltMode = False
                self.lasso_func = LassoInteractor(self.polydata)
            else:
                self.lassoSltMode = False
                self.lasso_func = None
        # 矩形刪除範圍
        elif self.key == "Delete" and self.boxSltMode:
            self.removeCells(self.boxArea.GetFrustum())
        # 點刪除範圍
        elif self.key == "Delete" and self.pointSltMode:
            self.keep_select_area(self.point_func.total_path_point)
            self.point_func.unRenderAllSelectors(self.renderer,self.GetInteractor())
        # 套索刪除範圍
        elif self.key == "Delete" and self.lassoSltMode:
            self.removeCells(self.lasso_func.loop)
            self.lasso_func.unRenderAllSelectors(self.renderer,self.GetInteractor())
        # 封閉點選取範圍
        elif self.key == "Return" and self.pointSltMode:
            self.point_func.closeArea(interactor, renderer)
        # 取消上一步選取 (undo)
        elif self.key == "z" and self.pointSltMode:
            self.point_func.undo(renderer, interactor)
        elif self.key == "z" and self.lassoSltMode:
            self.lasso_func.undo(renderer, interactor)
        # 還原上一步選取 (redo)
        elif self.key == "y" and self.pointSltMode:
            self.point_func.redo(renderer, interactor)
        elif self.key == "y" and self.lassoSltMode:
            self.lasso_func.redo(renderer, interactor)
        # 穿透模式切換
        elif self.key in ["t", "T"]:
            self.throughBtnMode = not self.throughBtnMode
            print(f"Through mode: {self.throughBtnMode}")

    def removeCells(self, selection_frustum):
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

    def keep_select_area(self, loop_points):
        if loop_points.GetNumberOfPoints() < 3:
            return

        # 使用 SelectPolyData 建立封閉區域選取
        select = vtk.vtkSelectPolyData()
        select.SetInputData(self.polydata)
        select.SetLoop(loop_points)
        select.GenerateSelectionScalarsOn()
        select.SetSelectionModeToSmallestRegion()
        select.Update()

        # 用 ClipPolyData 裁切選取區域
        clip = vtk.vtkClipPolyData()
        clip.SetInputConnection(select.GetOutputPort())
        clip.InsideOutOn()
        clip.Update()

        # 轉為 PolyData
        geometry = vtk.vtkGeometryFilter()
        geometry.SetInputConnection(clip.GetOutputPort())
        geometry.Update()

        new_poly_data = geometry.GetOutput()
        if new_poly_data.GetNumberOfCells() == 0:
            return

        self.renderer.RemoveActor(self.actor)
        self.mapper.SetInputData(new_poly_data)
        self.actor.SetMapper(self.mapper)
        self.actor.GetProperty().SetColor(1.0, 0.0, 0.0)
        self.renderer.AddActor(self.actor)
        self.polydata.DeepCopy(new_poly_data)
        self.GetInteractor().GetRenderWindow().Render()

    def onLeftButtonDown(self, obj, event):
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
            self.boxArea.AreaPick(self.start_position[0], self.start_position[1],
                                self.end_position[0], self.end_position[1], self.renderer)
            self.selection_frustum = self.boxArea.GetFrustum()

            if self.throughBtnMode:
                # 穿透模式：選取所有可見範圍
                self.extract = vtk.vtkExtractGeometry()
                self.extract.SetInputData(self.polydata)
                self.extract.SetImplicitFunction(self.selection_frustum)
                self.extract.ExtractInsideOn()
                self.extract.Update()
                self.selected = self.extract.GetOutput()
            else:
                # 非穿透模式：只選取表面
                self.extract = vtk.vtkExtractGeometry()
                self.extract.SetInputData(self.polydata)
                self.extract.SetImplicitFunction(self.selection_frustum)
                self.extract.ExtractBoundaryCellsOff()
                self.extract.Update()
                self.selected = self.extract.GetOutput()

            if self.selected.GetNumberOfCells() > 0:
                self.geometry_filter = vtk.vtkGeometryFilter()
                self.geometry_filter.SetInputData(self.selected)
                self.geometry_filter.Update()
                self.mapper.SetInputData(self.geometry_filter.GetOutput())
                self.actor.SetMapper(self.mapper)
                self.actor.GetProperty().SetColor(1.0, 0.0, 0.0)
                self.renderer.AddActor(self.actor)
            self.OnLeftButtonUp()
            self.GetInteractor().GetRenderWindow().Render()

