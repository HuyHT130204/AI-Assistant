$(document).ready(function () {
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
