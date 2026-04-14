# AR-Pyramid-Camera-Pose-Estimator
> A hybrid 3D AR projection tool supporting both offline video and live webcam modes using OpenCV.


본 프로젝트는 OpenCV를 활용하여 카메라의 3차원 자세를 추정하고, 
이를 바탕으로 체스보드 평면 위에 가상의 3D 입체 피라미드(Pyramid)를 증강현실(AR)로 투영하는 Python 스크립트입니다. 

단순한 오프라인 영상 처리를 넘어, **사용자의 파일 환경을 스스로 인식하여 3가지 모드(오프라인 / 웹캠 다이렉트 / 웹캠 캘리브레이션)로 자동 분기하는 시스템**을 구현했습니다.

## ⚙️ 핵심 기술 및 파이프라인

1. **자동 모드 스위칭 :**
   * `os.path.exists`를 활용하여 작업 디렉토리의 파일을 분석하고 최적의 환경을 자동으로 세팅합니다.
   * 번거로운 세팅 없이 코드 단 한 줄 실행으로 상황에 맞는 캘리브레이션 및 AR 렌더링이 진행됩니다.
    
2. **Camera Pose Estimation:**
   * 서브픽셀 단위(`cv2.cornerSubPix`)로 정밀 보정된 2D 이미지 좌표와, 실제 물리적 크기(`SQUARE_SIZE = 0.032m`)가 반영된 3D 월드 좌표 간의 관계를 바탕으로 PnP 알고리즘을 수행하여 카메라의 실시간 회전(Rotation) 및 이동(Translation) 벡터를 추정합니다.
3. **3D AR Object Projection):**
   * 평면적인 이미지가 아닌, 체스보드 바닥에서 $Z$축 방향으로 솟아오르는 **'3D 입체 피라미드'**의 정점 5개를 수학적으로 설계했습니다.
   * 계산된 카메라의 3D 자세를 바탕으로 가상 좌표들을 2D 이미지 평면에 투영시켜 오버레이합니다.

---

## 🎬 AR 렌더링 결과 데모

카메라의 움직임과 렌즈의 왜곡을 완벽하게 반영하여 원근감이 적용되는 실시간 3D 피라미드의 모습입니다.

![AR_Final_Result (1)](https://github.com/user-attachments/assets/e3d38496-bccc-4c4c-9e3d-c0cde26179bf)


---

## 🚀 실행 방법 (How to Run)

1. 본 저장소를 Clone 하거나 파일을 다운로드합니다.
2. 터미널(또는 명령 프롬프트)에서 해당 폴더로 이동하여 아래 명령어를 실행합니다.
```bash
python ar_pyramid_visualization.py
