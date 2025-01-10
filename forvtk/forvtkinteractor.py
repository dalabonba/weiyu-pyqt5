import vtk
class HighlightInteractorStyle(vtk.vtkInteractorStyleRubberBandPick):
    def __init__(self, parent=None):
        self.AddObserver("LeftButtonReleaseEvent", self.OnLeftButtonUpEvent)
        self.AddObserver("KeyPressEvent", self.OnKeyPress)
        self.pickingEnabled = False
        self.selectedCells = None  # To store selected cells for deletion

        self.SelectedMapper = vtk.vtkCompositePolyDataMapper2()
        self.SelectedActor = vtk.vtkActor()
        self.SelectedActor.SetMapper(self.SelectedMapper)
        self.SelectedActor.GetProperty().SetColor(1.0, 0.0, 0.0)  # Red

    def OnKeyPress(self, obj, event):
        key = self.GetInteractor().GetKeySym()
        # Toggle pickingEnabled when 'r' is pressed
        if key == 'r':
            self.pickingEnabled = not self.pickingEnabled
        # If 'Delete' key is pressed, delete the selected cells
        elif key == 'Delete' and self.selectedCells and self.selectedCells.GetNumberOfCells() > 0:
            self.DeleteSelectedCells()
    def SetPolyData(self, polydata):
        self.polydata = polydata

    def OnLeftButtonUpEvent(self, obj, event):
        if self.selectedCells is not None:
            self.GetInteractor().GetRenderWindow().GetRenderers().GetFirstRenderer().RemoveActor(self.SelectedActor)
            self.selectedCells = None
        self.SelectedMapper = vtk.vtkCompositePolyDataMapper2()
        self.SelectedActor = vtk.vtkActor()
        self.SelectedActor.SetMapper(self.SelectedMapper)
        self.SelectedActor.GetProperty().SetColor(1.0, 0.0, 0.0)  # Red
        # self.GetInteractor().GetRenderWindow().Render()
        self.OnLeftButtonUp()
        if self.pickingEnabled:
            frustum = self.GetInteractor().GetPicker().GetFrustum()

            # 使用 vtkIdFilter 來保留原始索引
            id_filter = vtk.vtkIdFilter()
            id_filter.SetInputData(self.polydata)
            id_filter.SetPointIds(False)
            id_filter.SetCellIds(True)  # 保留 Cell IDs
            id_filter.Update()

            # 更新 extract 使用處理過的資料
            self.extract = vtk.vtkExtractPolyDataGeometry()
            self.extract.SetInputData(id_filter.GetOutput())
            self.extract.SetImplicitFunction(frustum)
            self.extract.Update()

            # 取得篩選後的 PolyData
            selected_polydata = self.extract.GetOutput()
            selected_polydata.GetCellData().SetActiveScalars("vtkIdFilter_Ids")

            # 儲存篩選出的單元
            if selected_polydata.GetNumberOfCells() > 0:
                self.selectedCells = selected_polydata
                self.SelectedMapper.SetInputData(self.selectedCells)
                self.SelectedMapper.ScalarVisibilityOff()
                self.GetInteractor().GetRenderWindow().GetRenderers().GetFirstRenderer().AddActor(self.SelectedActor)
                self.GetInteractor().GetRenderWindow().Render()

    def DeleteSelectedCells(self):
        """
        Delete the selected cells from the original polydata using original cell IDs safely.
        """
        if self.selectedCells is not None and self.selectedCells.GetNumberOfCells() > 0:
            # 從選取的 PolyData 中取得原始索引
            original_ids = [
                int(self.selectedCells.GetCellData().GetScalars().GetTuple(i)[0]) 
                for i in range(self.selectedCells.GetNumberOfCells())
            ]

            # 建立一個 mask 標記要刪除的單元
            mask = vtk.vtkUnsignedCharArray()
            mask.SetName("Mask")
            mask.SetNumberOfComponents(1)
            mask.SetNumberOfTuples(self.polydata.GetNumberOfCells())
            mask.Fill(1)  # 預設為保留 (1)

            # 將需要刪除的單元標記為 0
            for cell_id in original_ids:
                mask.SetValue(cell_id, 0)

            # 將 mask 加入到 polydata 中
            self.polydata.GetCellData().AddArray(mask)
            self.polydata.GetCellData().SetActiveScalars("Mask")

            # 使用 vtkThreshold 過濾掉 Mask = 0 的單元 (刪除)
            threshold = vtk.vtkThreshold()
            threshold.SetInputData(self.polydata)
            threshold.ThresholdBetween(1, 1)  # 只保留 Mask = 1 的單元
            threshold.Update()

            # 使用 vtkGeometryFilter 將結果轉換回 polydata 格式
            geometry_filter = vtk.vtkGeometryFilter()
            geometry_filter.SetInputData(threshold.GetOutput())
            geometry_filter.Update()

            # 將處理後的 polydata 設置回 self.polydata
            self.polydata.DeepCopy(geometry_filter.GetOutput())
            self.polydata.Modified()

            self.SelectedMapper.SetInputData(self.polydata)
            self.reactor = vtk.vtkActor()
            self.reactor.SetMapper(self.SelectedMapper)
            self.reactor.GetProperty().SetColor((0.0, 1.0, 0.0))
            # self.SelectedMapper.ScalarVisibilityOff()  # 關閉標量可視化，使用單一顏色

            # 移除選取的單元的可視化
            self.GetInteractor().GetRenderWindow().GetRenderers().GetFirstRenderer().RemoveActor(self.SelectedActor)
            self.GetInteractor().GetRenderWindow().GetRenderers().GetFirstRenderer().AddActor(self.reactor)
            self.GetInteractor().GetRenderWindow().Render()


            print(f"已成功刪除 {len(original_ids)} 個單元")