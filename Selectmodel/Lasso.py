import vtk

# 套索選取類別
class LassoInteractor(vtk.vtkInteractorStyleTrackballCamera):
    def __init__(self,poly_data):
        super().__init__()
        self.poly_data = poly_data
        self.select_append = vtk.vtkAppendPolyData()
        self.empty_append = vtk.vtkAppendPolyData()
        self.select_poly_data = vtk.vtkPolyData()
        self.picker = vtk.vtkCellPicker()
        self.dijkstra_path = []
        self.pickpointId = []
        self.selection_point = vtk.vtkPoints()
        self.loop = vtk.vtkImplicitSelectionLoop()
        self.boundaryActors = []
        self.select_poly_data.SetPoints(self.selection_point)   
        self.AddObserver("LeftButtonPressEvent", self.onLeftButtonDown)
    # 滑鼠左鍵按下

    def onLeftButtonDown(self, obj, event, interactor, renderer):
        self.renderer = renderer
        self.interactor = interactor
        clickPos = interactor.GetEventPosition()

        
        self.picker.Pick(clickPos[0], clickPos[1], 0, renderer)
        picked_id = self.picker.GetPointId()
        if picked_id == -1:
            print("無效的點選取")
            return
        self.pickpointId.append(picked_id)

        self.selection_point.InsertNextPoint(self.picker.GetPickPosition())
        self.select_poly_data.SetPoints(self.selection_point)
        
        interactor.GetRenderWindow().Render()
            # 確保點足夠
        if len(self.pickpointId) < 3:
            print("點數不足，無法形成封閉區域")
            return
        self.select_append.RemoveAllInputs()  # 清除舊路徑
        self.dijkstra_path.clear()
        
        for i in range(len(self.pickpointId)):
            dijkstra = vtk.vtkDijkstraGraphGeodesicPath()
            dijkstra.SetInputData(self.poly_data)
            dijkstra.SetStartVertex(self.pickpointId[i])
            dijkstra.SetEndVertex(self.pickpointId[i-1])
            dijkstra.Update()
            self.dijkstra_path.append(dijkstra)
        
        
        for path in self.dijkstra_path:
            self.select_append.AddInputData(path.GetOutput())
        self.select_append.Update()
        self.boundary = self.select_append.GetOutput()

        if self.boundary.GetNumberOfPoints() > 2:
            first_point = self.boundary.GetPoint(0)
            self.boundary.GetPoints().InsertNextPoint(first_point)
        self.boundary.Modified()

        boundaryMapper = vtk.vtkPolyDataMapper()
        boundaryMapper.SetInputData(self.boundary)
        self.boundaryActor = vtk.vtkActor()
        self.boundaryActor.SetMapper(boundaryMapper)
        self.boundaryActor.GetProperty().SetRepresentationToWireframe()
        self.boundaryActor.GetProperty().SetLineWidth(2)
        self.boundaryActor.GetProperty().SetEdgeVisibility(True)
        self.boundaryActor.GetProperty().SetRenderLinesAsTubes(False)
        self.boundaryActor.GetProperty().SetLineStipplePattern(0xf0f0)
        self.boundaryActor.GetProperty().SetLineStippleRepeatFactor(1)
        self.boundaryActor.GetProperty().SetColor(1, 0, 0)
        self.boundaryActors.append(self.boundaryActor)
        renderer.AddActor(self.boundaryActor)
        interactor.GetRenderWindow().Render()
        if len(self.pickpointId) < 3:
            print("點數不足，無法形成封閉區域")
            return
        self.loop.SetLoop(self.boundary.GetPoints())
        
        clipper = vtk.vtkClipPolyData()
        clipper.SetInputData(self.poly_data)
        clipper.SetClipFunction(self.loop)
        clipper.InsideOutOn()
        clipper.Update()
        clipperMapper = vtk.vtkPolyDataMapper()
        clipperMapper.SetInputConnection(clipper.GetOutputPort())
        clipperActor = vtk.vtkActor()
        clipperActor.SetMapper(clipperMapper)
        renderer.AddActor(clipperActor)
        interactor.GetRenderWindow().Render()
        

        # 清除選取輔助樣式
    def unRenderAllSelectors(self,renderer,interactor):
        for actor in self.boundaryActors:
            renderer.RemoveActor(actor)
        self.boundaryActors.clear()

        self.selection_point.Reset()
        self.dijkstra_path.clear()
        self.pickpointId.clear()
        self.select_append.RemoveAllInputs()
        
        return
        