document.addEventListener('DOMContentLoaded', function() {
    // Đảm bảo chatHistory bị ẩn hoàn toàn khi khởi động
    const chatHistory = document.getElementById('chatHistory');
    if (chatHistory) {
        chatHistory.style.display = 'none';
        chatHistory.style.minHeight = "0";
        chatHistory.style.maxHeight = "0";
        chatHistory.style.margin = "0";
        chatHistory.style.padding = "0";
        chatHistory.style.border = "none";
        chatHistory.style.boxShadow = "none";
    }
    
    // Đảm bảo initialization-container hiển thị đúng
    const initContainer = document.querySelector('.initialization-container');
    if (initContainer) {
        initContainer.style.display = 'flex';
        initContainer.style.position = 'absolute';
        initContainer.style.top = '0';
        initContainer.style.left = '0';
        initContainer.style.width = '100%';
        initContainer.style.height = '100%';
        initContainer.style.zIndex = '100';
    }
    
    // Đảm bảo các thành phần quét nằm chính giữa
    const scanElements = document.querySelectorAll('#Loader, #FaceAuth, #FaceAuthSuccess, #HelloGreet');
    scanElements.forEach(el => {
        if (el) {
            el.style.position = 'absolute';
            el.style.top = '50%';
            el.style.left = '50%';
            el.style.transform = 'translate(-50%, -50%)';
            el.style.zIndex = '110';
        }
    });
    
    // Đảm bảo WishMessage hiển thị đúng ở dưới cùng
    const wishMessage = document.getElementById('WishMessage');
    if (wishMessage) {
        wishMessage.style.position = 'absolute';
        wishMessage.style.bottom = '5%';
        wishMessage.style.left = '0';
        wishMessage.style.width = '100%';
        wishMessage.style.textAlign = 'center';
        wishMessage.style.zIndex = '110';
    }
    
    // Đảm bảo universe-background hiển thị đúng
    const universeBackground = document.querySelector('.universe-background');
    if (universeBackground) {
        universeBackground.style.height = '100vh';
        universeBackground.style.display = 'flex';
        universeBackground.style.flexDirection = 'column';
        universeBackground.style.justifyContent = 'center';
        universeBackground.style.alignItems = 'center';
        universeBackground.style.position = 'relative';
        universeBackground.style.overflow = 'hidden';
    }
    
    // Add particles with enhanced properties
    const particles = document.getElementById('particles');
    for (let i = 0; i < 40; i++) {
        const particle = document.createElement('div');
        particle.className = 'particle';
        
        // Random sizes for particles
        const size = Math.random() * 4 + 2;
        particle.style.width = size + 'px';
        particle.style.height = size + 'px';
        
        // Position within heart area with depth
        particle.style.left = Math.random() * 300 + 50 + 'px';
        particle.style.top = Math.random() * 300 + 50 + 'px';
        particle.style.opacity = Math.random() * 0.7 + 0.3;
        
        // 3D transform for depth effect
        const zIndex = Math.floor(Math.random() * 50) - 25;
        particle.style.transform = `translateZ(${zIndex}px)`;
        
        // Add animation delay for twinkling effect
        particle.style.animationDelay = Math.random() * 3 + 's';
        particle.style.animationDuration = (Math.random() * 3 + 3) + 's';
        
        particles.appendChild(particle);
    }

    // Create sparkles that float up with enhanced effect
    function createSparkle() {
        const sparkle = document.createElement('div');
        sparkle.className = 'sparkle';
        
        // Position within the heart area
        const heartCenter = document.querySelector('.heart-center');
        if (heartCenter) {
            const rect = heartCenter.getBoundingClientRect();
            
            // Randomize position more widely
            sparkle.style.left = (Math.random() * 160 - 80 + rect.left + rect.width/2) + 'px';
            sparkle.style.top = (Math.random() * 160 - 80 + rect.top + rect.height/2) + 'px';
            
            // Randomize animation timing
            sparkle.style.animationDelay = Math.random() + 's';
            sparkle.style.animationDuration = (Math.random() * 2 + 2) + 's';
            
            // Randomize size
            const size = Math.random() * 3 + 1;
            sparkle.style.width = size + 'px';
            sparkle.style.height = size + 'px';
            
            document.body.appendChild(sparkle);
            
            // Remove sparkle after animation completes
            setTimeout(() => {
                sparkle.remove();
            }, 3000);
        }
    }

    // Create energy lines
    function createEnergyLines() {
        const heart = document.querySelector('.heart-container');
        
        // Create 6 energy lines at different angles
        for (let i = 0; i < 6; i++) {
            const line = document.createElement('div');
            line.className = 'energy-line';
            
            // Set random length
            const length = Math.random() * 60 + 60;
            line.style.width = length + 'px';
            
            // Delay animation
            line.style.animationDelay = (i * 1.3) + 's';
            
            heart.appendChild(line);
        }
    }
    
    // Add magical orbs that orbit around
    function createMagicalOrbs() {
        const heart = document.querySelector('.heart-container');
        
        // Create 5 magical orbs
        for (let i = 0; i < 5; i++) {
            const orb = document.createElement('div');
            orb.className = 'magical-orb';
            
            // Set random size
            const size = Math.random() * 4 + 3;
            orb.style.width = size + 'px';
            orb.style.height = size + 'px';
            
            // Set animation properties
            orb.style.animationDelay = (i * 2.5) + 's';
            orb.style.animationDuration = (Math.random() * 10 + 12) + 's';
            
            // Random orbit radius
            const radius = Math.random() * 40 + 80;
            orb.style.animationName = `orb-move`;
            orb.style.transform = `rotate(${i * 72}deg) translateX(${radius}px)`;
            
            heart.appendChild(orb);
        }
    }

    // Create nebula effect
    function createNebula() {
        const heart = document.querySelector('.heart-container');
        const nebula = document.createElement('div');
        nebula.className = 'heart-nebula';
        heart.appendChild(nebula);
    }

    // Create heart glow
    function createHeartGlow() {
        const heart = document.querySelector('.heart-container');
        const glow = document.createElement('div');
        glow.className = 'heart-glow';
        heart.appendChild(glow);
    }
    
    // Add additional heart border
    function createAdditionalBorder() {
        const heart = document.querySelector('.heart-container');
        const border = document.createElement('div');
        border.className = 'heart-border heart-border-4';
        heart.appendChild(border);
    }
    
    // Initialize all effects
    createEnergyLines();
    createMagicalOrbs();
    createNebula();
    createHeartGlow();
    createAdditionalBorder();
    
    // Create sparkles periodically
    setInterval(createSparkle, 200);
});

$(document).ready(function () {

  eel.init()()
  $('.text').textillate({
    loop: true,
    speed: 1500,
    sync: true,
    in: {
      effect: "bounceIn",
    },
    out: {
      effect: "bounceOut",
    },
  });

  // Xóa phần textillate cho siri-message
  // $(".siri-message").textillate({
  //   loop: true,
  //   sync: true,
  //   in: {
  //     effect: "fadeInUp",
  //     sync: true,
  //   },
  //   out: {
  //     effect: "fadeOutUp",
  //     sync: true,
  //   },
  // });

  var siriWave = new SiriWave({
    container: document.getElementById("siri-container"),
    width: 940,
    style: "ios9",
    amplitude: "1",
    speed: "0.30",
    height: 200,
    autostart: true,
    waveColor: "#ff0000",
    waveOffset: 0,
    rippleEffect: true,
    rippleColor: "#ffffff",
  });

  // Khai báo function giúp hiển thị lại UI sau khi xử lý xong
  eel.expose(ShowHood);
  function ShowHood() {
    $("#SiriWave").attr("hidden", true);
    $("#Oval").attr("hidden", false);
  }

  // Hiển thị tin nhắn từ trợ lý
  eel.expose(DisplayMessage);
  function DisplayMessage(message) {
    const siriMessage = $(".siri-message");
    siriMessage.removeAttr("style"); // Xóa mọi hiệu ứng cũ
    siriMessage.text(message);       // Hiển thị toàn bộ text ngay lập tức
  }

  // Hiển thị tin nhắn từ người dùng
  eel.expose(senderText);
  function senderText(message) {
    // Thêm code nếu cần hiển thị tin nhắn người dùng
    console.log("User said: " + message);
  }

  // Xử lý khi nhấn nút micro
  $("#MicBtn").click(function () {
    eel.play_assistant_sound();
    $("#Oval").attr("hidden", true);
    $("#SiriWave").attr("hidden", false);
    eel.takeAllCommand()();
  });

  // Xử lý phím tắt
  function doc_keyUp(e) {
    // Win + J để kích hoạt trợ lý
    if (e.key === "j" && e.metaKey) {
      eel.play_assistant_sound();
      $("#SiriWave").attr("hidden", false);
      eel.takeAllCommand()();
    }
    
    // Enter để gửi tin nhắn
    if (e.key === "Enter" && $("#chatbox").is(":focus")) {
      let message = $("#chatbox").val();
      if (message.trim() !== "") {
        PlayAssistant(message);
      }
    }
  }
  document.addEventListener("keyup", doc_keyUp, false);

  // Xử lý khi gửi tin nhắn văn bản
  function PlayAssistant(message) {
    if (message.trim() !== "") {
      $("#Oval").attr("hidden", true);
      $("#SiriWave").attr("hidden", false);
      eel.takeAllCommand(message);
      $("#chatbox").val("");
      $("#MicBtn").attr("hidden", false);
      $("#SendBtn").attr("hidden", true);
    } else {
      console.log("Empty message, nothing sent.");
    }
  }

  // Hiển thị/ẩn nút tùy theo trạng thái input
  function ShowHideButton(message) {
    if (message.length == 0) {
      $("#MicBtn").attr("hidden", false);
      $("#SendBtn").attr("hidden", true);
    } else {
      $("#MicBtn").attr("hidden", true);
      $("#SendBtn").attr("hidden", false);
    }
  }

  // Theo dõi thay đổi trong ô input
  $("#chatbox").keyup(function () {
    let message = $("#chatbox").val();
    console.log("Current chatbox input: ", message);
    ShowHideButton(message);
  });

  // Xử lý khi nhấn nút gửi
  $("#SendBtn").click(function () {
    let message = $("#chatbox").val();
    PlayAssistant(message);
  });

  // Đảm bảo các chức năng UI khác hoạt động
  $("#ChatBtn").click(function() {
    // Xử lý khi nhấn nút chat
    console.log("Chat button clicked");
  });

  // Xử lý khi nhấn nút cài đặt
  $("#SettingBtn").click(function() {
    // Hiệu ứng nút khi nhấn
    $(this).addClass("active-btn");
    setTimeout(() => {
      $(this).removeClass("active-btn");
    }, 300);
    
    // Hiển thị loader trước khi lấy dữ liệu
    $("#settingsModal .modal-body").html('<div class="text-center p-4"><div class="spinner-border text-primary" role="status"><span class="visually-hidden">Loading...</span></div><p class="mt-2">Loading settings...</p></div>');
    $("#settingsModal").modal("show");
    
    // Lấy cài đặt hiện tại từ backend với hiệu ứng loading
    setTimeout(() => {
      eel.get_assistant_settings()(function(settings) {
        // Tạo lại nội dung form
        $("#settingsModal .modal-body").html(`
          <form id="settingsForm">
            <div class="setting-section">
              <label for="assistantName" class="form-label"><i class="bi bi-robot me-2"></i>Assistant Name</label>
              <div class="input-group">
                <input type="text" class="form-control" id="assistantName" placeholder="Enter assistant name" value="${settings.assistant_name}">
                <span class="input-group-text"><i class="bi bi-pencil-fill"></i></span>
              </div>
            </div>

            <div class="setting-section">
              <label for="ownerName" class="form-label"><i class="bi bi-person-fill me-2"></i>Owner Name</label>
              <div class="input-group">
                <input type="text" class="form-control" id="ownerName" placeholder="Enter your name" value="${settings.owner_name}">
                <span class="input-group-text"><i class="bi bi-pencil-fill"></i></span>
              </div>
            </div>

            <div class="setting-section">
              <label for="volumeRange" class="form-label"><i class="bi bi-volume-up-fill me-2"></i>Volume</label>
              <input type="range" class="form-range" id="volumeRange" min="0" max="100" value="${settings.volume}">
              <div class="d-flex justify-content-between">
                <small><i class="bi bi-volume-mute-fill"></i></small>
                <small id="volumeValue">${settings.volume}%</small>
                <small><i class="bi bi-volume-up-fill"></i></small>
              </div>
            </div>

            <div class="setting-section">
              <label class="form-label"><i class="bi bi-mic-fill me-2"></i>Voice Type</label>
              <div class="voice-options">
                <div class="form-check form-check-inline">
                  <input class="form-check-input" type="radio" name="voiceType" id="maleVoice" value="male" ${settings.voice_type !== "female" ? "checked" : ""}>
                  <label class="form-check-label" for="maleVoice">
                    <i class="bi bi-gender-male me-1"></i> Male
                  </label>
                </div>
                <div class="form-check form-check-inline">
                  <input class="form-check-input" type="radio" name="voiceType" id="femaleVoice" value="female" ${settings.voice_type === "female" ? "checked" : ""}>
                  <label class="form-check-label" for="femaleVoice">
                    <i class="bi bi-gender-female me-1"></i> Female
                  </label>
                </div>
              </div>
            </div>
          </form>
        `);

        // Khởi tạo lại các sự kiện
        initializeSettingsEvents();
        
        // Hiệu ứng hiển thị từng phần tử
        $("#settingsForm .setting-section").each(function(index) {
          $(this).css({
            opacity: 0,
            transform: 'translateY(20px)'
          });
          
          setTimeout(() => {
            $(this).css({
              transition: 'all 0.4s ease',
              opacity: 1,
              transform: 'translateY(0)'
            });
          }, 100 * (index + 1));
        });
      });
    }, 500); // Delay để tạo hiệu ứng loading
  });

  // Khởi tạo các sự kiện cho form cài đặt
  function initializeSettingsEvents() {
    // Cập nhật giá trị âm lượng khi kéo thanh trượt
    $("#volumeRange").on("input", function() {
      const value = $(this).val();
      $("#volumeValue").text(value + "%");
      
      // Thay đổi biểu tượng âm lượng tùy theo giá trị
      const volumeIcon = $(".bi-volume-up-fill, .bi-volume-down-fill, .bi-volume-off-fill", $(this).closest(".setting-section")).not(".me-2");
      volumeIcon.removeClass("bi-volume-up-fill bi-volume-down-fill bi-volume-off-fill");
      
      if (value > 70) {
        volumeIcon.addClass("bi-volume-up-fill");
      } else if (value > 20) {
        volumeIcon.addClass("bi-volume-down-fill");
      } else {
        volumeIcon.addClass("bi-volume-off-fill");
      }
    });
    
    // Hiệu ứng hover cho các phần input
    $(".input-group").hover(
      function() {
        $(this).find(".input-group-text").css({
          "background": "rgba(187, 134, 252, 0.3)",
          "border-color": "rgba(187, 134, 252, 0.5)"
        });
      },
      function() {
        $(this).find(".input-group-text").css({
          "background": "",
          "border-color": ""
        });
      }
    );
  }

  // Xử lý khi lưu cài đặt
  $("#saveSettings").click(function() {
    // Thêm hiệu ứng loading
    const originalText = $(this).html();
    $(this).html('<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>Saving...');
    $(this).prop("disabled", true);
    
    const settings = {
        assistant_name: $("#assistantName").val(),
        owner_name: $("#ownerName").val(),
        volume: parseInt($("#volumeRange").val()),
        voice_type: $("input[name='voiceType']:checked").val()
    };
    
    // Lưu cài đặt vào backend
    eel.save_assistant_settings(settings)(function(success) {
        setTimeout(() => {
          if (success) {
            // Hiển thị hiệu ứng thành công
            $("#saveSettings").html('<i class="bi bi-check-lg me-2"></i>Saved');
            $("#saveSettings").removeClass("btn-primary").addClass("btn-success");
            
            setTimeout(() => {
              // Đóng modal sau 1s
              $("#settingsModal").modal("hide");
              
              // Khôi phục nút sau khi đóng modal
              setTimeout(() => {
                $("#saveSettings").html(originalText);
                $("#saveSettings").removeClass("btn-success").addClass("btn-primary");
                $("#saveSettings").prop("disabled", false);
              }, 300);
              
              // Thông báo thành công
              eel.speak("Settings saved successfully");
            }, 1000);
          } else {
            // Hiển thị thông báo lỗi
            $("#saveSettings").html('<i class="bi bi-exclamation-triangle me-2"></i>Error');
            $("#saveSettings").removeClass("btn-primary").addClass("btn-danger");
            
            setTimeout(() => {
              $("#saveSettings").html(originalText);
              $("#saveSettings").removeClass("btn-danger").addClass("btn-primary");
              $("#saveSettings").prop("disabled", false);
            }, 2000);
          }
        }, 800); // Giả lập độ trễ của mạng
    });
  });

  // Khởi tạo sự kiện khi trang đã tải xong
  initializeSettingsEvents();
});
