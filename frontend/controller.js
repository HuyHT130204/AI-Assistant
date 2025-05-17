$(document).ready(function () {
    // Display Speak Message
    eel.expose(DisplayMessage);
    function DisplayMessage(message) {
      $(".siri-message").text(message);
    }

    eel.expose(ShowHood);
    function ShowHood() {
        $("#Oval").attr("hidden", false);
        $("#SiriWave").attr("hidden", true);
  }

  eel.expose(senderText);
  function senderText(message) {
    var chatBox = document.getElementById("chat-canvas-body");
    if (message.trim() !== "") {
      chatBox.innerHTML += `<div class="row justify-content-end mb-4">
          <div class = "width-size">
          <div class="sender_message">${message}</div>
      </div>`;

      chatBox.scrollTop = chatBox.scrollHeight;
    }
  }

  eel.expose(receiverText);
  function receiverText(message) {
    var chatBox = document.getElementById("chat-canvas-body");
    if (message.trim() !== "") {
      chatBox.innerHTML += `<div class="row justify-content-start mb-4">
          <div class = "width-size">
          <div class="receiver_message">${message}</div>
          </div>
      </div>`;

      // Scroll to the bottom of the chat box
      chatBox.scrollTop = chatBox.scrollHeight;
    }
  }

  eel.expose(hideLoader);
  function hideLoader() {
    $("#Loader").attr("hidden", true);
    $("#FaceAuth").attr("hidden", false);
  }
  // Hide Face auth and display Face Auth success animation
  eel.expose(hideFaceAuth);
  function hideFaceAuth() {
    $("#FaceAuth").attr("hidden", true);
    $("#FaceAuthSuccess").attr("hidden", false);
  }

  // Hide success and display
  eel.expose(hideFaceAuthSuccess);
  function hideFaceAuthSuccess() {
    $("#FaceAuthSuccess").attr("hidden", true);
    $("#HelloGreet").attr("hidden", false);
  }

  eel.expose(hideStart);
  function hideStart() {
      $("#Start").attr("hidden", true);
  }
  
  // Hide Start Page and display blob
  eel.expose(showMainInterface);
  function showMainInterface() {
      // Ẩn tất cả các phần không cần thiết
      $("#Loader").attr("hidden", true);
      $("#FaceAuth").attr("hidden", true);
      $("#FaceAuthSuccess").attr("hidden", true);
      $("#HelloGreet").attr("hidden", true);
      $("#Start").attr("hidden", true);
      
      // Hiển thị giao diện chính với hiệu ứng
      setTimeout(function () {
        $("#Oval").addClass("animate__animated animate__zoomIn");
        $("#Oval").attr("hidden", false);
      }, 500);
  }
});
