import vtk

class LassoInteractor(vtk.vtkInteractorStyleTrackballCamera):
    def __init__(self, poly_data):
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
        # 新增功能：支援 undo 和 redo
        self.redoPickpointId = []
        self.redoDijkstraPath = []
        self.redoBoundaryActors = []
        self.select_poly_data.SetPoints(self.selection_point)
        self.AddObserver("LeftButtonPressEvent", self.onLeftButtonDown)

    def onLeftButtonDown(self, obj, event, interactor, renderer):
        self.renderer = renderer
        self.interactor = interactor
        
        clickPos = interactor.GetEventPosition()
        self.picker.Pick(clickPos[0], clickPos[1], 0, renderer)
        self.pickpointId.append(self.picker.GetPointId())
        for i in range(len(self.pickpointId)):
            # 實體化最短路徑
            dijkstra = vtk.vtkDijkstraGraphGeodesicPath()
            # 設定最短路徑的輸入資料
            dijkstra.SetInputData(self.poly_data)
            # 最短路徑最後一點為選取的點
            dijkstra.SetStartVertex(self.pickpointId[i])
            # 最短路徑第一點為選取的點
            dijkstra.SetEndVertex(self.pickpointId[i-1])
            # 更新最短路徑
            dijkstra.Update()
            # 存放最短路徑
            self.dijkstra_path.append(dijkstra)
        # 複製最短路徑資料給self.boundary
        for path in self.dijkstra_path:
            # 視覺化套索線段
            self.select_append.AddInputData(path.GetOutput())
        # 更新視覺化套索線段
        self.select_append.Update()
        # boundary列表儲存視覺化套索線段資料
        self.boundary = self.select_append.GetOutput()     
        # 實體化選取範圍要放入的映射器變數
        boundaryMapper = vtk.vtkPolyDataMapper()
        # 映射器放入boundary列表
        boundaryMapper.SetInputData(self.boundary)
        # 選取範圍要放入的渲染物件變數
        self.boundaryActor = vtk.vtkActor()
        # 渲染物件放入映射器
        self.boundaryActor.SetMapper(boundaryMapper)
        # 設定選取範圍的線寬
        self.boundaryActor.GetProperty().SetLineWidth(2)
        # 設定選取範圍線段的顏色為紅色
        self.boundaryActor.GetProperty().SetColor(1, 0, 0)
        # 視覺化線段套索要清除效果放入的列表
        self.boundaryActors.append(self.boundaryActor)
        # 渲染器放入視覺化線段套索
        self.renderer.AddActor(self.boundaryActor)
        # 小於3個點不做事
        if len(self.pickpointId) < 3:
            return
        # 選取範圍資料
        self.loop.SetLoop(self.boundary.GetPoints())
        # 更新視窗
        self.GetInteractor().GetRenderWindow().Render()

    def unRenderAllSelectors(self, renderer, interactor):
        for actor in self.boundaryActors:
            renderer.RemoveActor(actor)
        self.boundaryActors.clear()
        self.selection_point.Reset()
        self.dijkstra_path.clear()
        self.pickpointId.clear()
        self.select_append.RemoveAllInputs()
        interactor.GetRenderWindow().Render()

    def undo(self):
        interactor = self.GetInteractor()
        renderer = interactor.GetRenderer()
        if not self.pickpointId:
            return
        # 儲存用於 redo
        last_pickpointId = self.pickpointId.pop()
        self.redoPickpointId.append(last_pickpointId)
        if self.dijkstra_path:
            self.redoDijkstraPath.append(self.dijkstra_path.copy())
            self.dijkstra_path.clear()
        if self.boundaryActors:
            last_actor = self.boundaryActors.pop()
            self.redoBoundaryActors.append(last_actor)
            renderer.RemoveActor(last_actor)
        self.selection_point.Reset()
        self.select_append.RemoveAllInputs()
        interactor.GetRenderWindow().Render()

    def redo(self):
        interactor = self.GetInteractor()
        renderer = interactor.GetRenderer()
        if self.redoPickpointId:
            redo_pickpointId = self.redoPickpointId.pop()
            self.pickpointId.append(redo_pickpointId)
        if self.redoDijkstraPath:
            redo_dijkstra_path = self.redoDijkstraPath.pop()
            self.dijkstra_path = redo_dijkstra_path
               # redo視覺化線段
        if self.redoBoundaryActors:
            # 拿出undo的視覺化線段資料
            redo_boundary_actor = self.redoBoundaryActors.pop()
            # 將undo資料添加回視覺化線段列表
            self.boundaryActors.append(redo_boundary_actor)
            # 渲染器放入視覺化線段
            self.renderer.AddActor(redo_boundary_actor)
        # 更新視窗
        self.GetInteractor().GetRenderWindow().Render()