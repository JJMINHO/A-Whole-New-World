# A-Whole-New-World
This program is an AR tool that is based on your video.

# AR-Pyramid-Camera-Pose-Estimator

본 프로젝트는 OpenCV를 활용하여 카메라의 3차원 자세(Pose)를 추정하고, 이를 바탕으로 체스보드 평면 위에 가상의 3D 입체 피라미드(Pyramid)를 증강현실(AR)로 투영하는 Python 스크립트입니다. 

특히 본 프로젝트는 **[오프라인 데모]**와 **[실시간 라이브 웹캠]** 환경을 모두 지원하는 **하이브리드(Hybrid) 스위칭 구조**로 설계되어 있어, 별도의 설정 없이도 최적의 AR 렌더링 환경을 자동으로 구성합니다.

## ⚙️ 구현 알고리즘 및 핵심 기술

1. **자동화된 카메라 캘리브레이션 (Camera Calibration):**
   * 미리 캘리브레이션된 파라미터 파일(`calib_result_webcam.npz`)이 존재할 경우, 연산 부하를 최소화하기 위해 해당 데이터를 즉시 메모리에 로드합니다.
   * 만약 파일이 존재하지 않는 경우, 즉시 라이브 웹캠을 켜고 **자동으로 40장의 체스보드 코너(`cv2.findChessboardCorners`) 데이터를 수집**하여 즉석에서 렌즈의 내부 파라미터 행렬($K$)과 왜곡 계수($dist$)를 도출 및 저장합니다.
2. **Camera Pose Estimation (`cv2.solvePnP`):**
   * 서브픽셀 단위(`cv2.cornerSubPix`)로 정밀 보정된 2D 이미지 좌표와, 실제 물리적 크기(`SQUARE_SIZE = 0.032m`)가 반영된 3D 월드 좌표 간의 관계를 바탕으로 PnP 알고리즘을 수행하여 카메라의 실시간 회전(Rotation) 및 이동(Translation) 벡터를 추정합니다.
3. **AR Object Projection (`cv2.projectPoints`):**
   * 단순한 2D 평면 드로잉 예제를 넘어, $Z$축 방향(음수)으로 솟아오르는 **'3D 피라미드(Pyramid)'** 형태의 3차원 구조물을 수학적 정점(Vertex)으로 설계했습니다.
   * 계산된 카메라의 3D 자세를 바탕으로 이 3D 좌표들을 2D 이미지 평면에 투영시켜 현실 영상에 오버레이 하였습니다.

---

## 🎬 AR 렌더링 결과 데모

카메라의 움직임과 렌즈의 왜곡을 완벽하게 반영하여 원근감이 적용되는 실시간 3D 피라미드의 모습입니다.




---

## 🚀 실행 방법 (How to Run)

1. 본 저장소를 Clone 하거나 파일을 다운로드합니다.
2. 터미널(또는 명령 프롬프트)에서 해당 폴더로 이동합니다.
3. 터미널에 아래 명령어를 입력하여 프로그램을 실행합니다.
```bash
python ar_pyramid_visualization.py
