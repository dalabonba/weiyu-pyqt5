#include <vtkSmartPointer.h>
#include <vtkPLYReader.h>
#include <vtkAppendPolyData.h>
#include <vtkCleanPolyData.h>
#include <vtkActor.h>
#include <vtkPolyDataMapper.h>
#include <vtkRenderer.h>
#include <vtkRenderWindow.h>
#include <vtkRenderWindowInteractor.h>
#include <vtkPLYWriter.h>
#include <vtkTransformPolyDataFilter.h>
#include <vtkWindowToImageFilter.h>
#include <vtkImageResize.h>
#include <vtkImageShiftScale.h>
#include <vtkPNGWriter.h>
#include <vtkCamera.h>
#include <vtkAutoInit.h>
#include <vtkInteractorStyleTrackballCamera.h>
#include <vtkProperty.h>
#include <vtkTransform.h>
#include <experimental/filesystem>
#include <vtkBoundingBox.h>
#include <vtkPlaneSource.h>
#include <math.h>

// 初始化 VTK 模組
VTK_MODULE_INIT(vtkRenderingOpenGL2);
VTK_MODULE_INIT(vtkInteractionStyle);

// 命名空間別名
namespace fs = std::experimental::filesystem;

int main() {
	// 匯出缺陷和對咬牙的深度圖，確保咬合位置正確
	std::vector<std::string> folderNames = { "Four-Surface", "Onlay", "Single-Surface", "Three-Surface", "Two-Surface" };
	// 設定缺陷和對咬牙的路徑

	// 設定輸出深度圖的資料夾路徑
	std::string outputDirectory = "D://Users//user//Desktop//weiyundontdelete//GANdata//trainingdepth//0817//";
	std::string ouputdata = "Down";


	// 創建vtkAppendPolyData和vtkCleanPolyData過濾器
	vtkSmartPointer<vtkAppendPolyData> appendFilter1 = vtkSmartPointer<vtkAppendPolyData>::New();
	vtkSmartPointer<vtkAppendPolyData> appendFilter2 = vtkSmartPointer<vtkAppendPolyData>::New();
	vtkSmartPointer<vtkAppendPolyData> appendFilter3 = vtkSmartPointer<vtkAppendPolyData>::New();
	vtkSmartPointer<vtkCleanPolyData> cleanFilter1 = vtkSmartPointer<vtkCleanPolyData>::New();
	vtkSmartPointer<vtkCleanPolyData> cleanFilter2 = vtkSmartPointer<vtkCleanPolyData>::New();
	vtkSmartPointer<vtkCleanPolyData> cleanFilter3 = vtkSmartPointer<vtkCleanPolyData>::New();
	for (const std::string& folderName : folderNames) {
		// 設定缺陷和對咬牙的路徑
		std::string path1 = "D://Users//user//Desktop//weiyundontdelete//GANdata//training//" + folderName + "//Down//";
		std::string path2 = "D://Users//user//Desktop//weiyundontdelete//GANdata//training//" + folderName + "//Up//";
		// 迭代處理缺陷和對咬牙的文件
		for (const auto &entry1 : fs::directory_iterator(path1)) {
			if (fs::is_regular_file(entry1)) {
				std::string fileName1 = entry1.path().filename().string();
				// 在對咬牙的文件中查找相同的文件
				for (const auto &entry2 : fs::directory_iterator(path2)) {
					if (fs::is_regular_file(entry2)) {
						std::string fileName2 = entry2.path().filename().string();
						// 如果找到相同的文件
						if (fileName1 == fileName2) {
                            vtkSmartPointer<vtkRenderer> renderer = vtkSmartPointer<vtkRenderer>::New();
                            vtkSmartPointer<vtkRenderWindow> renderWindow = vtkSmartPointer<vtkRenderWindow>::New();
                            vtkSmartPointer<vtkRenderWindowInteractor> renderWindowInteractor = vtkSmartPointer<vtkRenderWindowInteractor>::New();
                            
                            renderWindow->SetSize(256, 256);
                            renderer->SetBackground(0, 0, 0);
                            renderWindow->AddRenderer(renderer);
                            renderWindowInteractor->SetRenderWindow(renderWindow);


							// 讀取缺陷模型
							vtkSmartPointer<vtkPLYReader> reader = vtkSmartPointer<vtkPLYReader>::New();
							reader->SetFileName((path1 + fileName1).c_str());
							reader->Update();
							
							// 讀取對咬牙模型
							vtkSmartPointer<vtkPLYReader> reader1 = vtkSmartPointer<vtkPLYReader>::New();
							reader1->SetFileName((path2 + fileName2).c_str());
							reader1->Update();

							
							// 創建第一個模型的vtkActor和vtkPolyDataMapper
							vtkSmartPointer<vtkActor> actor1 = vtkSmartPointer<vtkActor>::New();
							vtkSmartPointer<vtkPolyDataMapper> mapper1 = vtkSmartPointer<vtkPolyDataMapper>::New();
							mapper1->SetInputConnection(reader->GetOutputPort());
							actor1->SetMapper(mapper1);
							actor1->GetProperty()->SetColor(0.0, 1.0, 0.0); // 設置第一個模型的顏色
							//actor1->GetProperty()->SetOpacity(0); // 透明度0
							
							
							// 創建第二個模型的vtkActor和vtkPolyDataMapper
							vtkSmartPointer<vtkActor> actor2 = vtkSmartPointer<vtkActor>::New();
							vtkSmartPointer<vtkPolyDataMapper> mapper2 = vtkSmartPointer<vtkPolyDataMapper>::New();
							mapper2->SetInputConnection(reader1->GetOutputPort());
							actor2->SetMapper(mapper2);
							actor2->GetProperty()->SetColor(1.0, 0.0, 0.0); // 設置第二個模型的顏色
							actor2->GetProperty()->SetOpacity(0); // 設置第二個模型的透明度

							// 將模型的Actor添加到渲染器
							renderer->AddActor(actor1);
							renderer->AddActor(actor2);


							//創建polydata用來存Boundingbox資料，Getbound會將X、Y、Z最小與最大都記錄。
							vtkSmartPointer<vtkPolyData> polyData = vtkSmartPointer<vtkPolyData>::New();
							polyData = cleanFilter1->GetOutput();
                            double bounds[6], bounds1[6];
                            reader->GetOutput()->GetBounds(bounds);
                            reader1->GetOutput()->GetBounds(bounds1);
							double minX = bounds[0];
							double maxX = bounds[1];
							double minY = bounds[2];
							double maxY = bounds[3];
							double minZ = bounds[4];
							double maxZ = bounds[5];
							double center1[3] = { (bounds[0] + bounds[1]) / 2, (bounds[2] + bounds[3]) / 2, (bounds[4] + bounds[5]) / 2 };

							vtkSmartPointer<vtkPolyData> polyData1 = vtkSmartPointer<vtkPolyData>::New();
							reader1->GetOutput()->GetBounds(bounds1);
							double minX1 = bounds1[0];
							double maxX1 = bounds1[1];
							double minY1 = bounds1[2];
							double maxY1 = bounds1[3];
							double minZ1 = bounds1[4];
							double maxZ1 = bounds1[5];
							double center2[3] = { (bounds1[0] + bounds1[1]) / 2, (bounds1[2] + bounds1[3]) / 2, (bounds1[4] + bounds1[5]) / 2 };

							// 啟動渲染窗口
							vtkSmartPointer<vtkInteractorStyleTrackballCamera> style = vtkSmartPointer<vtkInteractorStyleTrackballCamera>::New();
							renderWindowInteractor->SetInteractorStyle(style);
							renderWindow->Render();


							vtkCamera* cam1 = renderer->GetActiveCamera();
							//近遠裁減平面數值紀錄
							cam1->SetFocalPoint(center1);
							cam1->SetParallelProjection(true); // 啟用正交投影模式
							double camPosition[3];
							cam1->GetPosition(camPosition);

							//Get camera to model center
							double distancecamre_bb = sqrt(pow(camPosition[0]- center1[0],2)+ pow(camPosition[1] - center1[1],2)+ pow(camPosition[2] - center1[2],2)) ;
							double distancecamre_bbup = sqrt(pow(camPosition[0] - center2[0], 2) + pow(camPosition[1] - center2[1], 2) + pow(camPosition[2] - center2[2], 2));
							double gapanddown = distancecamre_bb - distancecamre_bbup;
							double near = distancecamre_bb - ((maxZ - minZ)*0.5);
							double far = distancecamre_bb + ((maxZ - minZ)*0.5);

							
							//這邊為了計算Bounding 最長Y值，為了找到最適合的裁剪平面
							cam1->SetParallelScale(((maxY - minY)*0.5)); // 這裡的boundinglong是模型Y軸上的最大間距，SetParallelScale方法是用來設置平行投影的視口尺度
							if (ouputdata =="Up")
							{
								cam1->SetClippingRange(near - gapanddown, far);
							}
							else
							{
								cam1->SetClippingRange(near , far);
							}
			
							renderer->SetActiveCamera(cam1);
							// 創建vtkWindowToImageFilter以獲取渲染窗口深度圖
							vtkSmartPointer<vtkWindowToImageFilter> depthImageFilter = vtkSmartPointer<vtkWindowToImageFilter>::New();
							depthImageFilter->SetInput(renderWindow);
							depthImageFilter->SetInputBufferTypeToZBuffer();

							// 創建vtkImageShiftScale以將深度值映射到0-255的範圍
							vtkSmartPointer<vtkImageShiftScale> scaleFilter = vtkSmartPointer<vtkImageShiftScale>::New();
							scaleFilter->SetInputConnection(depthImageFilter->GetOutputPort());
							scaleFilter->SetOutputScalarTypeToUnsignedChar();
							scaleFilter->SetShift(-1);
							scaleFilter->SetScale(-255);

							// 設置輸出深度圖的文件路徑
							//std::string outputFilePath = outputDirectory + folderName + "//Prep//" + fileName1.substr(0, fileName1.find(".")) + ".png";
							std::string outputFilePath = outputDirectory +  "//" +ouputdata+"//" + fileName1.substr(0, fileName1.find(".")) + ".png";

							// 創建vtkPNGWriter以保存深度圖像
							vtkSmartPointer<vtkPNGWriter> depthImageWriter = vtkSmartPointer<vtkPNGWriter>::New();
							depthImageWriter->SetFileName(outputFilePath.c_str());
							depthImageWriter->SetInputConnection(scaleFilter->GetOutputPort());
							depthImageWriter->Write();
						}
					}
				}
			}
		}


	}
	return 0;
}
