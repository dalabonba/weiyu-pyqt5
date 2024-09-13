#include <vtkSmartPointer.h>
#include <vtkPNGReader.h>
#include <vtkImageData.h>
#include <vtkImageCast.h>
#include <vtkAutoInit.h>
#include <vtkPNGWriter.h>
#include <iostream>
#include <string>
#include <vector>
#include <fstream>
#include <experimental/filesystem>
namespace fs = std::experimental::filesystem;
VTK_MODULE_INIT(vtkRenderingOpenGL2);
VTK_MODULE_INIT(vtkInteractionStyle);
int main() {
	std::string ouputDirectory = "D://Users//user//Desktop//doublemodeldo//now//testmask//"; // 輸出深度圖的資料夾路徑
	std::string inputDirectory = "D://Users//user//Desktop//doublemodeldo//now//combinemask//"; // 輸出深度圖的資料夾路徑
	for (const auto &entry1 : fs::directory_iterator(inputDirectory)) {
		if (fs::is_regular_file(entry1)) {
			std::string fileName1 = entry1.path().filename().string();
			// 读取图像
			vtkSmartPointer<vtkPNGReader> reader = vtkSmartPointer<vtkPNGReader>::New();
			reader->SetFileName((inputDirectory + fileName1).c_str());
			reader->Update();

			vtkSmartPointer<vtkImageData> image = reader->GetOutput();

			// 定义颜色值
			unsigned char blue[3] = { 0, 0, 255 };  // 蓝色
			unsigned char yellow[3] = { 100, 100, 0 };  // 黄色
			unsigned char red[3] = { 2, 0, 0 };  // 红色

			int dimensions[3];
			image->GetDimensions(dimensions);

			bool foundYellow = false; // 標記是否找到了黃色
			int startX = 0; // 起點的x坐標
			int endX = 0; // 終點的x坐標
			bool startXSet = false; // 标记是否已经设置过startX
			for (int y = 0; y < dimensions[1]; y++) {

				for (int x = 0; x < dimensions[0]; x++) {
					unsigned char* pixel = static_cast<unsigned char*>(image->GetScalarPointer(x, y, 0));

					// 如果遇到黃色像素，標記foundYellow為true並設定起點
					if (pixel[0] != 0 && pixel[1] != 0 && pixel[2] == yellow[2]) {
						if (startXSet != true) {
							startX = x;
						}
						foundYellow = true;

						startXSet = true;
					}

					// 如果已經找到了黃色，繼續尋找紅色像素，將其x座標作為終點
					if (foundYellow) {
						if (pixel[0] != 0 && pixel[1] == red[1] && pixel[2] == red[2]) {
							endX = x;
							break;
						}
					}
				}

				// 如果找到了黃色和紅色，將起點到終點之間的像素塗成藍色
				if (foundYellow && endX > startX) {
					for (int x = startX; x <= endX; x++) {
						unsigned char* pixel = static_cast<unsigned char*>(image->GetScalarPointer(x, y, 0));
						pixel[0] = blue[0];
						pixel[1] = blue[1];
						pixel[2] = blue[2];
					}
				}

				// 清除標記以準備尋找下一個黃色像素
				foundYellow = false;
				startXSet = false;
			}
			//拿掉黃跟紅的部分
			for (int y = 0; y < dimensions[1]; y++) {
				for (int x = 0; x < dimensions[0]; x++) {
					unsigned char* pixel = static_cast<unsigned char*>(image->GetScalarPointer(x, y, 0));
					if (pixel[0] != 0 && pixel[1] != 0 && pixel[2] == 0) {
						pixel[0] = 0;
						pixel[1] = 0;
						pixel[2] = 0;
					}
					else if (pixel[0] != 0 && pixel[1] == 0 && pixel[2] == 0) {
						pixel[0] = 0;
						pixel[1] = 0;
						pixel[2] = 0;
					}
				}
			}


			// 保存处理后的图像
			vtkSmartPointer<vtkImageCast> caster = vtkSmartPointer<vtkImageCast>::New();
			caster->SetInputData(image);
			caster->SetOutputScalarTypeToUnsignedChar();
			std::string outputFilePath = ouputDirectory + fileName1 ;
			vtkSmartPointer<vtkPNGWriter> outputWriter = vtkSmartPointer<vtkPNGWriter>::New();
			outputWriter->SetFileName(outputFilePath.c_str());
			outputWriter->SetInputConnection(caster->GetOutputPort());
			outputWriter->Write();
		}
	}

	return 0;
}
