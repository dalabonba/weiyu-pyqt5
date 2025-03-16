import vtk

# 點選取類別
class PointInteractor(vtk.vtkInteractorStyleTrackballCamera):
    def __init__(self,poly_data):
        super().__init__()
        self.poly_data = poly_data
        self.dijkstra = vtk.vtkDijkstraGraphGeodesicPath()
        self.selectionPoints = vtk.vtkPoints()
        self.dijkstra.SetInputData(self.poly_data)
        self.sphereActors = []
        self.lineActors = []
        self.pathList = []
        self.meshNumList = []
        self.loop = vtk.vtkImplicitSelectionLoop()
        self.total_length = 0

        self.AddObserver("LeftButtonPressEvent", self.onLeftButtonDown)
    # 滑鼠左鍵按下
    def onLeftButtonDown(self,obj,event,interactor,renderer):
        clickPos = interactor.GetEventPosition()
        picker = vtk.vtkCellPicker()
        picker.Pick(clickPos[0],clickPos[1],0,renderer)
        if(picker.GetCellId() != -1):
            # 視覺化選取點
            self.pathList.append(picker.GetPointId())
            point_position = self.poly_data.GetPoint(picker.GetPointId())
            sphereSource = vtk.vtkSphereSource()
            sphereSource.SetCenter(point_position)
            sphereSource.SetRadius(0.02)
            sphereMapper = vtk.vtkPolyDataMapper()
            sphereMapper.SetInputConnection(sphereSource.GetOutputPort())
            self.sphereActor = vtk.vtkActor()
            self.sphereActor.SetMapper(sphereMapper)
            self.sphereActor.GetProperty().SetColor(1.0, 0.0, 0.0)
            renderer.AddActor(self.sphereActor)
            self.sphereActors.append(self.sphereActor)
            
            # 求最小路徑
            if len(self.pathList) > 1:
                self.dijkstra.SetStartVertex(self.pathList[-2])
                self.dijkstra.SetEndVertex(self.pathList[-1])
                self.dijkstra.Update()

                idList = self.dijkstra.GetIdList()
                self.meshNumList.append(idList.GetNumberOfIds())
                for i in range(idList.GetNumberOfIds() - 1):
                    # 視覺化選取線
                    id0 = idList.GetId(i)
                    id1 = idList.GetId(i + 1)
                    
                    self.line = vtk.vtkLineSource()
                    self.line.SetPoint1(self.poly_data.GetPoint(id0))
                    self.line.SetPoint2(self.poly_data.GetPoint(id1))
                    lineMapper = vtk.vtkPolyDataMapper()
                    lineMapper.SetInputConnection(self.line.GetOutputPort())
                    self.lineActor = vtk.vtkActor()
                    self.lineActor.SetMapper(lineMapper)
                    self.lineActor.GetProperty().SetColor(1.0, 0.0, 0.0)
                    renderer.AddActor(self.lineActor)
                    self.lineActors.append(self.lineActor)
                
            interactor.GetRenderWindow().Render()

    # 封閉選取範圍
    def closeArea(self,interactor,renderer):
        if self.pathList[0] == self.pathList[-1]:
            self.selectionPoints.SetNumberOfPoints(len(self.pathList))
            for i in range(len(self.pathList)):
                self.selectionPoints.SetPoint(i,self.poly_data.GetPoint(self.pathList[i]))
            self.loop.SetLoop(self.selectionPoints)
            clip = vtk.vtkClipPolyData()
            clip.SetInputData(self.poly_data)
            clip.SetClipFunction(self.loop)
            clip.InsideOutOn()

            clipMapper = vtk.vtkPolyDataMapper()
            clipMapper.SetInputConnection(clip.GetOutputPort())

            backProp = vtk.vtkProperty()
            backProp.SetColor(1.0, 0.0, 0.0)

            clipActor = vtk.vtkActor()
            clipActor.SetMapper(clipMapper)
            clipActor.SetProperty(backProp)

            renderer.AddActor(clipActor)
            interactor.GetRenderWindow().Render()
    # 清除選取輔助樣式
    def unRenderAllSelectors(self,renderer,interactor):
        for actor in self.sphereActors:
            renderer.RemoveActor(actor)
        self.sphereActors.clear()
        for actor in self.lineActors:
            renderer.RemoveActor(actor)
        self.pathList = []
        self.lineActors.clear()
        interactor.GetRenderWindow().Render()
    # 取消上一步選取
    def cancelLastSelection(self,renderer,interactor):
        for _ in range(self.meshNumList[-1]):
            renderer.RemoveActor(self.lineActors[-1])
            self.lineActors.pop()   
            if len(self.pathList) > 0:
                renderer.RemoveActor(self.sphereActors[-1])
                self.sphereActors.pop()
                print(f"sphereActors:{len(self.sphereActors)}")
                self.pathList.pop()

            interactor.GetRenderWindow().Render() 