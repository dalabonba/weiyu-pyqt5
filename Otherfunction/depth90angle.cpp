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
#include <vtkIntersectionPolyDataFilter.h>
#include <vtkCamera.h>
#include <vtkAutoInit.h>
#include <vtkInteractorStyleTrackballCamera.h>
#include <vtkProperty.h>
#include <vtkIterativeClosestPointTransform.h>
#include <vtkLandmarkTransform.h>
#include <vtkTransform.h>
#include <vtkCenterOfMass.h>
#include <vtkBooleanOperationPolyDataFilter.h>
#include <experimental/filesystem>

// 初始化 VTK 模組
VTK_MODULE_INIT(vtkRenderingOpenGL2);
VTK_MODULE_INIT(vtkInteractionStyle);

// 命名空間別名
namespace fs = std::experimental::filesystem;

int main() {
	// 匯出缺陷和對咬牙的深度圖，確保咬合位置正確
	//std::vector<std::string> folderNames = { "Four-Surface", "Onlay", "Single-Surface", "Three-Surface", "Two-Surface" };
	std::vector<std::string> folderNames = { "Three-Surface" };

	// 設定缺陷和對咬牙的路徑

	// 設定輸出深度圖的資料夾路徑
	std::string outputDirectory = "D://Users//user//Desktop//weiyundontdelete//GANdata//trainingdepth//depth90//";
	std::string outputtype = "Down";

	// 創建vtkAppendPolyData和vtkCleanPolyData過濾器
	vtkSmartPointer<vtkAppendPolyData> appendFilter1 = vtkSmartPointer<vtkAppendPolyData>::New();
	vtkSmartPointer<vtkAppendPolyData> appendFilter2 = vtkSmartPointer<vtkAppendPolyData>::New();
	vtkSmartPointer<vtkAppendPolyData> appendFilter3 = vtkSmartPointer<vtkAppendPolyData>::New();
	vtkSmartPointer<vtkCleanPolyData> cleanFilter1 = vtkSmartPointer<vtkCleanPolyData>::New();
	vtkSmartPointer<vtkCleanPolyData> cleanFilter2 = vtkSmartPointer<vtkCleanPolyData>::New();
	vtkSmartPointer<vtkCleanPolyData> cleanFilter3 = vtkSmartPointer<vtkCleanPolyData>::New();
	for (const std::string& folderName : folderNames) {
		// 設定缺陷和對咬牙的路徑
		std::string path1 = "D://Users//user//Desktop//weiyundontdelete//GANdata//training//" + folderName + "//"+outputtype+"//";
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
							// 清空過濾器的連接，準備添加新的模型
							cleanFilter1->RemoveAllInputConnections(0);
							cleanFilter2->RemoveAllInputConnections(0);
							cleanFilter3->RemoveAllInputConnections(0);
							appendFilter1->RemoveAllInputConnections(0);
							appendFilter2->RemoveAllInputConnections(0);
							appendFilter3->RemoveAllInputConnections(0);

							// 讀取缺陷模型
							vtkSmartPointer<vtkPLYReader> reader = vtkSmartPointer<vtkPLYReader>::New();
							reader->SetFileName((path1 + fileName1).c_str());
							reader->Update();

							// 讀取對咬牙模型
							vtkSmartPointer<vtkPLYReader> reader1 = vtkSmartPointer<vtkPLYReader>::New();
							reader1->SetFileName((path2 + fileName2).c_str());
							reader1->Update();

							// 獲取缺陷模型中心位置
							vtkSmartPointer<vtkCenterOfMass> centerOfMassFilter1 = vtkSmartPointer<vtkCenterOfMass>::New();
							centerOfMassFilter1->SetInputData(reader->GetOutput());
							centerOfMassFilter1->Update();
							double positiondown[3];
							centerOfMassFilter1->GetCenter(positiondown);

							// 獲取對咬牙模型中心位置
							vtkSmartPointer<vtkCenterOfMass> centerOfMassFilter2 = vtkSmartPointer<vtkCenterOfMass>::New();
							centerOfMassFilter2->SetInputData(reader1->GetOutput());
							centerOfMassFilter2->Update();
							double positionup[3];
							centerOfMassFilter2->GetCenter(positionup);
							//先定位0,0,0，並旋轉Y-90，之後平移到下排原始位置
							vtkSmartPointer<vtkTransform> transform = vtkSmartPointer<vtkTransform>::New();
							transform->Translate(-positiondown[0], -positiondown[1], -positiondown[2]);
							transform->RotateY(90);
							transform->Translate(positiondown[0], positiondown[1], positiondown[2]);

							vtkSmartPointer<vtkTransformPolyDataFilter> transformFilter = vtkSmartPointer<vtkTransformPolyDataFilter>::New();
							transformFilter->SetInputData(reader->GetOutput());
							transformFilter->SetTransform(transform);
							transformFilter->Update();


							//appendFilter1->AddInputConnection(reader->GetOutputPort());
							cleanFilter1->SetInputConnection(transformFilter->GetOutputPort());
							cleanFilter1->Update();

							appendFilter2->AddInputConnection(reader1->GetOutputPort());
							cleanFilter2->SetInputConnection(appendFilter2->GetOutputPort());
							cleanFilter2->Update();
							//// 合併兩個vtkPolyData
							appendFilter3->AddInputConnection(reader->GetOutputPort());
							appendFilter3->AddInputConnection(reader1->GetOutputPort());
							cleanFilter3->SetInputConnection(appendFilter3->GetOutputPort());
							cleanFilter3->Update();


							// 建立PolyDataMapper
							vtkSmartPointer<vtkPolyDataMapper> mapper1 = vtkSmartPointer<vtkPolyDataMapper>::New();
							mapper1->SetInputConnection(cleanFilter1->GetOutputPort());

							vtkSmartPointer<vtkPolyDataMapper> mapper2 = vtkSmartPointer<vtkPolyDataMapper>::New();
							mapper2->SetInputConnection(cleanFilter2->GetOutputPort());

							// 建立Actor
							vtkSmartPointer<vtkActor> actor = vtkSmartPointer<vtkActor>::New();
							actor->SetMapper(mapper1);

							vtkSmartPointer<vtkActor> actor1 = vtkSmartPointer<vtkActor>::New();
							actor1->SetMapper(mapper2);
							actor1->GetProperty()->SetOpacity(0);



							vtkSmartPointer<vtkRenderer> renderer = vtkSmartPointer<vtkRenderer>::New();
							vtkSmartPointer<vtkRenderWindow> renderWindow = vtkSmartPointer<vtkRenderWindow>::New();

							// 將模型的Actor添加到渲染器
							renderer->AddActor(actor);
							/*	renderer->AddActor(actor1);*/
								//這邊設置視窗256*256背景黑色
							renderWindow->SetSize(256, 256);
							renderer->SetBackground(0, 0, 0);
							renderer->ResetCamera();
							renderWindow->AddRenderer(renderer);
							vtkSmartPointer<vtkRenderWindowInteractor> renderWindowInteractor = vtkSmartPointer<vtkRenderWindowInteractor>::New();
							renderWindowInteractor->SetRenderWindow(renderWindow);


							//創建polydata用來存Boundingbox資料，Getbound會將X、Y、Z最小與最大都記錄。
							vtkSmartPointer<vtkPolyData> polyData = vtkSmartPointer<vtkPolyData>::New();
							polyData = cleanFilter1->GetOutput();
							double bounds[6];
							polyData->GetBounds(bounds);
							double minX = bounds[0];
							double maxX = bounds[1];
							double minY = bounds[2];
							double maxY = bounds[3];
							double minZ = bounds[4];
							double maxZ = bounds[5];
							double center1[3] = { (bounds[0] + bounds[1]) / 2, (bounds[2] + bounds[3]) / 2, (bounds[4] + bounds[5]) / 2 };
							if (fileName1 == "data0004.ply") {
								printf("123");
							}
							// 啟動渲染窗口
							vtkSmartPointer<vtkInteractorStyleTrackballCamera> style = vtkSmartPointer<vtkInteractorStyleTrackballCamera>::New();
							renderWindowInteractor->SetInteractorStyle(style);
							renderWindow->Render();


							vtkCamera* cam1 = vtkCamera::New();
							cam1 = renderer->GetActiveCamera();

							//近遠裁減平面數值紀錄
							double clip[2] = { 0 };
							cam1->GetClippingRange(clip);
							cam1->SetFocalPoint(center1);
							cam1->SetParallelProjection(true); // 啟用正交投影模式

							//這邊為了計算Bounding 最長Y值，為了找到最適合的裁剪平面
							double boundinglongscale = maxY - minY;;
							double boundinglongdepth = (maxX - minX);
							cam1->SetParallelScale((boundinglongscale)/2 + 0.1); // 這裡的boundinglong是模型Y軸上的最大間距，SetParallelScale方法是用來設置平行投影的視口尺度

							////這邊為了獲得相機到焦點的距離
							double clp_dis = clip[1] - clip[0]; // 	//這裡是算出投影平面間的距離（clp_dis）
							cam1->SetClippingRange(clip[0], clip[1]-clp_dis*0.5);
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
							std::string outputFilePath = outputDirectory  + fileName1.substr(0, fileName1.find(".")) + ".png";

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
