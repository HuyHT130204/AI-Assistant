document.addEventListener('DOMContentLoaded', function() {
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

  $(".siri-message").textillate({
    loop: true,
    sync: true,
    in: {
      effect: "fadeInUp",
      sync: true,
    },
    out: {
      effect: "fadeOutUp",
      sync: true,
    },
  });

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
    $(".siri-message").text(message);
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
    eel.takeAllCommand()();  // Đảm bảo tên function đúng
  });

  // Xử lý phím tắt
  function doc_keyUp(e) {
    // Win + J để kích hoạt trợ lý
    if (e.key === "j" && e.metaKey) {
      eel.play_assistant_sound();
      $("#Oval").attr("hidden", true);
      $("#SiriWave").attr("hidden", false);
      eel.takeAllCommand()();  // Đảm bảo tên function đúng
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
      eel.takeAllCommand(message);  // Đảm bảo tên function đúng
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

  $("#SettingBtn").click(function() {
    // Xử lý khi nhấn nút cài đặt
    console.log("Settings button clicked");
  });
});
