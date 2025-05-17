// Biến để kiểm soát trạng thái của hộp thoại FaceID
let faceIdDialogShown = false;
let authFailedDialogShown = false;
let faceIdChecked = false; // Biến để theo dõi việc kiểm tra FaceID
let authenticationInProgress = false; // Biến để theo dõi trạng thái đang xác thực

// Hàm kiểm tra FaceID ngay khi trang được tải
function checkFaceIdStatus() {
    if (!faceIdChecked) {
        faceIdChecked = true;
        // Gọi hàm Python để kiểm tra trạng thái FaceID
        eel.check_face_id_exists()(function(exists) {
            if (exists) {
                console.log("FaceID đã tồn tại, chuyển sang xác thực");
                // Nếu đã có dữ liệu FaceID, tiến hành xác thực
                if (!authenticationInProgress) {
                    authenticationInProgress = true;
                    eel.authenticate_user();
                }
            } else {
                console.log("FaceID chưa tồn tại, hiển thị hộp thoại thiết lập");
                // Nếu chưa có dữ liệu, hiển thị hộp thoại thiết lập
                showFaceIdSetupDialog();
            }
        });
    }
}

// Hiển thị hộp thoại thiết lập FaceID
eel.expose(showFaceIdSetupDialog);
function showFaceIdSetupDialog() {
    if (!faceIdDialogShown) {
        faceIdDialogShown = true;
        // Hiển thị overlay và hộp thoại
        document.getElementById('faceIdSetupOverlay').style.display = 'flex';
        document.getElementById('faceIdSetupDialog').style.display = 'flex';
        return true;
    }
    return false;
}

// Hiển thị hộp thoại thông báo FaceID là bắt buộc
eel.expose(showRequiredFaceIdDialog);
function showRequiredFaceIdDialog() {
    // Ẩn overlay thiết lập nếu đang hiển thị
    document.getElementById('faceIdSetupOverlay').style.display = 'none';
    faceIdDialogShown = false;
    // Hiện overlay và dialog Face ID Required
    document.getElementById('faceIdRequiredOverlay').style.display = 'flex';
    document.getElementById('faceIdRequiredDialog').style.display = 'flex';
    // Tự động ẩn sau 3 giây và hiển thị lại hộp thoại thiết lập
    setTimeout(function() {
        document.getElementById('faceIdRequiredOverlay').style.display = 'none';
        document.getElementById('faceIdRequiredDialog').style.display = 'none';
        showFaceIdSetupDialog();
    }, 3000);
}

// Hiển thị hộp thoại khi xác thực thất bại
eel.expose(showAuthFailedDialog);
function showAuthFailedDialog() {
    authenticationInProgress = false;
    if (!authFailedDialogShown) {
        authFailedDialogShown = true;
        document.getElementById('authFailedOverlay').style.display = 'flex';
        document.getElementById('authFailedDialog').style.display = 'flex';
    }
}

// Ẩn hộp thoại xác thực thất bại
eel.expose(hideAuthFailedDialog);
function hideAuthFailedDialog() {
    document.getElementById('authFailedOverlay').style.display = 'none';
    document.getElementById('authFailedDialog').style.display = 'none';
    authFailedDialogShown = false;
}

// Xử lý khi người dùng đồng ý thiết lập FaceID
function setupFaceId() {
    // Hiển thị thông báo đang thiết lập
    document.getElementById('faceIdSetupDialog').style.display = 'none';
    document.getElementById('faceIdSetupProgress').style.display = 'flex';
    
    // Gọi hàm Python để thiết lập FaceID
    eel.setup_face_id();
}

// Xử lý khi người dùng bỏ qua thiết lập FaceID
function skipFaceIdSetup() {
    // Gọi hàm Python để xử lý việc bỏ qua thiết lập
    eel.skip_face_id_setup();
}

// Xử lý khi người dùng muốn thử lại xác thực
function retryAuthentication() {
    if (!authenticationInProgress) {
        authenticationInProgress = true;
        eel.retry_authentication();
    }
}

// Ẩn hộp thoại thiết lập FaceID
eel.expose(hideFaceIdSetupDialog);
function hideFaceIdSetupDialog() {
    document.getElementById('faceIdSetupOverlay').style.display = 'none';
    faceIdDialogShown = false;
}

// Hiển thị hộp thoại khởi động lại
function showRestartDialog() {
    document.getElementById('restartOverlay').style.display = 'flex';
    document.getElementById('restartDialog').style.display = 'flex';
}

// Ẩn hộp thoại khởi động lại
function hideRestartDialog() {
    document.getElementById('restartOverlay').style.display = 'none';
    document.getElementById('restartDialog').style.display = 'none';
}

// Hàm hiển thị dialog thông báo cần mở lại app
function showManualRestartDialog() {
    document.getElementById('manualRestartOverlay').style.display = 'flex';
    document.getElementById('manualRestartDialog').style.display = 'flex';
}

eel.expose(onFaceIdSetupComplete);
function onFaceIdSetupComplete(success) {
    // Ẩn thông báo đang thiết lập
    document.getElementById('faceIdSetupProgress').style.display = 'none';
    if (success) {
        document.getElementById('faceIdSetupSuccess').style.display = 'none';
        hideFaceIdSetupDialog();
        showManualRestartDialog();
    } else {
        document.getElementById('faceIdSetupError').style.display = 'flex';
        setTimeout(function() {
            document.getElementById('faceIdSetupError').style.display = 'none';
            document.getElementById('faceIdSetupDialog').style.display = 'flex';
        }, 2000);
    }
}

// Hàm được gọi khi người dùng bỏ qua thiết lập FaceID
eel.expose(onFaceIdSetupSkipped);
function onFaceIdSetupSkipped() {
    // Thông báo đã bỏ qua thiết lập FaceID
    console.log("FaceID setup skipped");
}

// Hiển thị giao diện chính
eel.expose(showMainInterface);
function showMainInterface() {
    authenticationInProgress = false;
    document.getElementById('mainInterface').style.display = 'flex';
}

// Ẩn màn hình khởi động
eel.expose(hideStart);
function hideStart() {
    document.getElementById('startScreen').style.display = 'none';
}

// Khởi tạo khi trang được tải
document.addEventListener('DOMContentLoaded', function() {
    // Thiết lập các trình xử lý sự kiện
    document.getElementById('setupFaceIdBtn').addEventListener('click', setupFaceId);
    document.getElementById('skipFaceIdBtn').addEventListener('click', skipFaceIdSetup);
    
    // Thêm xử lý cho nút thử lại xác thực và thoát
    document.getElementById('retryAuthBtn').addEventListener('click', retryAuthentication);
    document.getElementById('exitAppBtn').addEventListener('click', function() {
        eel.exit_application();
    });
    
    // Thêm xử lý cho nút khởi động lại
    document.getElementById('restartBtn').addEventListener('click', restartSystem);
    
    // Kiểm tra trạng thái FaceID khi trang được tải
    // Thêm độ trễ để đảm bảo tất cả các yếu tố DOM đã được tải
    setTimeout(function() {
        checkFaceIdStatus();
    }, 300);
});