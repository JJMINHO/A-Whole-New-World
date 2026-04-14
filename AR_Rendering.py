import cv2
import numpy as np
import os
from datetime import datetime

# 체스보드 관련 기본 설정 값
VIDEO_FILE = 'chessboard.mp4'
CALIB_FILE = 'calib_result.npz'
WEBCAM_CALIB_FILE = 'calib_result_webcam.npz'
PATTERN_SIZE = (8, 6)
SQUARE_SIZE = 0.032

# 3D 공간상의 체스보드 실제 코너 좌표 생성 (Z=0 평면)
objp = np.zeros((PATTERN_SIZE[0] * PATTERN_SIZE[1], 3), np.float32)
objp[:, :2] = np.mgrid[0:PATTERN_SIZE[0], 0:PATTERN_SIZE[1]].T.reshape(-1, 2)
objp *= SQUARE_SIZE

# 피라미드의 3차원 좌표 정의
axis = np.float32([
    [2 * SQUARE_SIZE, 2 * SQUARE_SIZE, 0],
    [5 * SQUARE_SIZE, 2 * SQUARE_SIZE, 0],
    [5 * SQUARE_SIZE, 5 * SQUARE_SIZE, 0],
    [2 * SQUARE_SIZE, 5 * SQUARE_SIZE, 0],
    #위 4줄은 밑변
    [3.5 * SQUARE_SIZE, 3.5 * SQUARE_SIZE, -4 * SQUARE_SIZE]
    #피라미드 꼭짓점 부분
])

# 피라미드를 그리는 함수
def draw_pyramid(img, imgpts):
    imgpts = np.int32(imgpts).reshape(-1, 2)
    img = cv2.drawContours(img, [imgpts[:4]], -1, (0, 255, 0), 3)
    for i in range(4):
        img = cv2.line(img, tuple(imgpts[i]), tuple(imgpts[4]), (255, 100, 0), 3)
    img = cv2.circle(img, tuple(imgpts[4]), 8, (0, 0, 255), -1)
    return img

# 파일 존재 여부에 따른 모드 자동 스위칭
# 총 3가지 모드 구현
use_saved_files = os.path.exists(CALIB_FILE) and os.path.exists(VIDEO_FILE)

# 기존의 파일을 활용하는 케이스
if os.path.exists(CALIB_FILE) and os.path.exists(VIDEO_FILE):
    print(f"기존 파일('{CALIB_FILE}', '{VIDEO_FILE}')을 발견")
    print(" -> [오프라인 모드] 저장된 영상과 데이터로 AR 렌더링을 시작")

    with np.load(CALIB_FILE) as data:
        K = data['K']
        dist = data['dist']
    cap = cv2.VideoCapture(VIDEO_FILE)
    is_offline_video = True  # 👈 영상 파일일 경우 True로 변경

# 이전에 웹캠으로 캘리브레이션 해둔 파일이 있는 경우
elif os.path.exists(WEBCAM_CALIB_FILE):
    print(f"✅ 기존 웹캠 파라미터('{WEBCAM_CALIB_FILE}')를 발견했습니다.")
    print(" -> [모드 2] 라이브캠 다이렉트 모드: 캘리브레이션을 생략하고 즉시 AR을 시작합니다.")

    with np.load(WEBCAM_CALIB_FILE) as data:
        K, dist = data['K'], data['dist']
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("❌ 웹캠을 찾을 수 없습니다. 프로그램을 종료합니다.")
        exit()

# 라이브캠 모드
else:
    print(f"⚠️ 기존 파라미터 또는 영상 파일이 없습니다.")
    print(" -> [라이브캠 모드] 실시간 캘리브레이션 및 AR을 시작합니다.")

    cap = cv2.VideoCapture(0)  # 0번(기본 웹캠) 실행
    if not cap.isOpened():
        print("❌ 웹캠을 찾을 수 없습니다. 프로그램을 종료합니다.")
        exit()

    print("\n📷 웹캠을 향해 체스보드를 비춰주세요! (자동으로 데이터를 수집합니다)")
    objpoints = []
    imgpoints = []
    success_frames = 0
    frame_count = 0

# 라이브캠 모드에서 총 40장의 프레임 수집 및 캘리브레이션 값 추출
    while success_frames < 40:
        ret, frame = cap.read()
        if not ret: break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # 5프레임에 한 번씩 탐색
        if frame_count % 5 == 0:
            ret_corners, corners = cv2.findChessboardCorners(gray, PATTERN_SIZE, None)
            if ret_corners:
                criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
                corners2 = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
                objpoints.append(objp)
                imgpoints.append(corners2)
                success_frames += 1
                cv2.drawChessboardCorners(frame, PATTERN_SIZE, corners2, ret_corners)

        cv2.putText(frame, f'Calibrating... {success_frames}/40', (30, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 165, 255),
                    2)
        cv2.imshow('Live Calibration', frame)
        cv2.waitKey(1)
        frame_count += 1

    cv2.destroyWindow('Live Calibration')
    print("✅ 데이터 수집 완료! 캘리브레이션 연산 중")
    rms, K, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)

    np.savez('calib_result_webcam.npz', K=K, dist=dist)
    print(f"✅ 웹캠 파라미터 산출 및 저장 완료 (RMS Error: {rms:.4f})\n")

# AR 피라미드 시각화 및 동영상 저장
print("🚀 [AR 렌더링 모드] 체스보드 위에 3D 피라미드를 렌더링")
print(" - 's': 현재 화면 캡처, 'q': 종료")

# 영상 저장 설정
fps = cap.get(cv2.CAP_PROP_FPS)
if fps == 0 or np.isnan(fps): fps = 30  # 웹캠 연결 시 fps 값을 못 가져오는 에러 방지

width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter('AR_Final_Result.mp4', fourcc, fps, (width, height))

while True:
    ret, frame = cap.read()
    if not ret: break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # 매 프레임마다 체스보드의 위치를 찾는 과정
    ret_corners, corners = cv2.findChessboardCorners(gray, PATTERN_SIZE, None)

    if ret_corners:
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
        corners2 = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)

        # 3D Pose 추정 및 투영
        ret_pnp, rvecs, tvecs = cv2.solvePnP(objp, corners2, K, dist)
        imgpts, jac = cv2.projectPoints(axis, rvecs, tvecs, K, dist)

        frame = draw_pyramid(frame, imgpts)
        cv2.putText(frame, 'AR Tracking: ON', (30, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    else:
        cv2.putText(frame, 'AR Tracking: LOST', (30, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    cv2.imshow('AR Object Visualization', frame)
    out.write(frame)

    # 오프라인 영상은 원래 속도대로, 실시간 웹캠은 지연 없이(1ms) 재생
    delay = int(1000 / fps) if use_saved_files else 1
    key = cv2.waitKey(delay) & 0xFF

    if key == ord('q'):
        break
    elif key == ord('s') or key == ord('S'):
        time_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        img_name = f'AR_Capture_{time_str}.jpg'
        cv2.imwrite(img_name, frame)
        print(f"캡처 완료: {img_name}")

# 메모리 해제
cap.release()
out.release()
cv2.destroyAllWindows()