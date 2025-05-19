$(document).ready(function () {
    // Biến kiểm soát việc ghi lịch sử chat
    let shouldSaveHistory = false;
    
    // Đảm bảo chatHistory bị ẩn khi khởi động
    $("#chatHistory").hide();
    
    // Thiết lập sự kiện đóng khi click ra ngoài offcanvas
    $(document).on('click', function(e) {
      // Nếu offcanvas đang mở và click không phải vào offcanvas và không phải vào nút mở offcanvas
      if ($('#offcanvasScrolling').hasClass('show') && 
          !$(e.target).closest('#offcanvasScrolling').length && 
          !$(e.target).closest('#ChatBtn').length) {
        
        // Đóng offcanvas
        var offcanvasInstance = bootstrap.Offcanvas.getInstance(document.getElementById('offcanvasScrolling'));
        if (offcanvasInstance) {
          offcanvasInstance.hide();
        }
      }
    });
    
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

  // Hàm lấy thời gian hiện tại theo định dạng HH:MM
  function getCurrentTime() {
    const now = new Date();
    const hours = String(now.getHours()).padStart(2, '0');
    const minutes = String(now.getMinutes()).padStart(2, '0');
    return `${hours}:${minutes}`;
  }

  // Cho phép backend bật chế độ lưu lịch sử
  eel.expose(enableChatHistory);
  function enableChatHistory() {
    shouldSaveHistory = true;
    // Xóa lịch sử cũ khi mới vào để tránh hiển thị các tin nhắn ban đầu
    clearChatHistory();
    console.log("Chat history enabled");
    
    // Cập nhật trạng thái hiển thị của chat history
    updateChatHistoryVisibility();
  }
  
  // Cho phép backend tắt chế độ lưu lịch sử
  eel.expose(disableChatHistory);
  function disableChatHistory() {
    shouldSaveHistory = false;
    console.log("Chat history disabled");
  }
  
  // Cập nhật trạng thái hiển thị của chat history dựa trên nội dung
  function updateChatHistoryVisibility() {
    const chatHistoryContent = document.getElementById("chatHistoryContent");
    const chatHistory = document.getElementById("chatHistory");
    
    if (chatHistoryContent && chatHistory) {
      if (chatHistoryContent.children.length > 0) {
        // Có tin nhắn trong lịch sử, hiển thị chatHistory
        $(chatHistory).fadeIn(300);
        chatHistory.style.minHeight = "auto";
        chatHistory.style.maxHeight = "300px";
        chatHistory.style.margin = "15px 0";
        chatHistory.style.padding = "15px";
        chatHistory.style.border = "1px solid rgba(138, 43, 226, 0.15)";
      } else {
        // Không có tin nhắn, ẩn hoàn toàn chatHistory
        $(chatHistory).fadeOut(300);
        chatHistory.style.minHeight = "0";
        chatHistory.style.maxHeight = "0";
        chatHistory.style.margin = "0";
        chatHistory.style.padding = "0";
        chatHistory.style.border = "none";
      }
    }
  }
  
  // Xóa lịch sử chat
  eel.expose(clearChatHistory);
  function clearChatHistory() {
    const chatHistory = document.getElementById("chatHistoryContent");
    if (chatHistory) {
      chatHistory.innerHTML = '';
    }
    const chatBox = document.getElementById("chat-canvas-body");
    if (chatBox) {
      chatBox.innerHTML = '';
    }
    
    // Cập nhật trạng thái hiển thị
    updateChatHistoryVisibility();
  }

  // Hàm thêm tin nhắn vào cả hai vị trí (chatbox và chatHistory)
  function addMessageToHistory(isUser, message, time) {
    // Nếu không nên lưu lịch sử và là tin nhắn của assistant, bỏ qua
    if (!shouldSaveHistory && !isUser) {
      return;
    }
    
    if (!time) time = getCurrentTime();
    
    // CSS class cho tin nhắn dựa trên người gửi
    const messageClass = isUser ? "sender_message" : "receiver_message";
    const justifyClass = isUser ? "justify-content-end" : "justify-content-start";
    
    // HTML cho tin nhắn
    const messageHTML = `
      <div class="row ${justifyClass} mb-4">
        <div class="width-size">
          <div class="${messageClass}">${message}
            <div class="message-time">${time}</div>
          </div>
        </div>
      </div>`;
    
    // Thêm vào chatbox menu bằng cách tối ưu DOM
    const chatBox = document.getElementById("chat-canvas-body");
    if (chatBox) {
      // Tạo phần tử tạm thời để giảm thiểu reflow
      const tempDiv = document.createElement('div');
      tempDiv.innerHTML = messageHTML;
      while (tempDiv.firstChild) {
        chatBox.appendChild(tempDiv.firstChild);
      }
      
      // Sử dụng requestAnimationFrame để tối ưu hiệu năng cuộn
      requestAnimationFrame(() => {
        chatBox.scrollTop = chatBox.scrollHeight;
      });
    }
    
    // Thêm vào lịch sử chat trên trang chính một cách tối ưu
    const chatHistory = document.getElementById("chatHistoryContent");
    if (chatHistory) {
      // Sử dụng fragment để cải thiện hiệu suất
      const fragment = document.createDocumentFragment();
      const tempDiv = document.createElement('div');
      tempDiv.innerHTML = messageHTML;
      
      while (tempDiv.firstChild) {
        fragment.appendChild(tempDiv.firstChild);
      }
      chatHistory.appendChild(fragment);
      
      // Giới hạn số lượng tin nhắn hiển thị trong chatHistory (giữ 5 tin nhắn mới nhất)
      const maxMessages = 5;
      const messages = chatHistory.querySelectorAll(".row");
      if (messages.length > maxMessages) {
        // Xóa các tin nhắn cũ
        for (let i = 0; i < messages.length - maxMessages; i++) {
          if (messages[i] && messages[i].parentNode) {
            messages[i].parentNode.removeChild(messages[i]);
          }
        }
      }
      
      // Cuộn xuống dưới với requestAnimationFrame để tối ưu hiệu năng
      const historyContainer = document.getElementById("chatHistory");
      if (historyContainer) {
        requestAnimationFrame(() => {
          historyContainer.scrollTop = historyContainer.scrollHeight;
        });
      }
      
      // Cập nhật trạng thái hiển thị của chat history
      updateChatHistoryVisibility();
    }
  }

  eel.expose(senderText);
  function senderText(message) {
    if (message.trim() !== "") {
      // Tin nhắn người dùng luôn được lưu vào lịch sử
      addMessageToHistory(true, message);
      
      // Kiểm tra và dọn dẹp khi chat quá dài
      checkAndCleanupChats();
    }
  }

  eel.expose(receiverText);
  function receiverText(message) {
    if (message.trim() !== "") {
      // Chỉ thêm tin nhắn của assistant vào lịch sử khi flag được bật
      addMessageToHistory(false, message);
      
      // Kiểm tra và dọn dẹp khi chat quá dài
      checkAndCleanupChats();
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
      
      // Bật chế độ lưu lịch sử chat khi vào giao diện chính
      enableChatHistory();
      
      // Hiển thị giao diện chính với hiệu ứng
      setTimeout(function () {
        $("#Oval").addClass("animate__animated animate__zoomIn");
        $("#Oval").attr("hidden", false);
      }, 500);
  }

  // Hàm dọn dẹp và giới hạn số lượng tin nhắn để tránh vấn đề về hiệu suất
  function checkAndCleanupChats() {
    const chatBox = document.getElementById("chat-canvas-body");
    if (chatBox) {
      const messages = chatBox.querySelectorAll(".row");
      const maxSidebarMessages = 50; // Giữ tối đa 50 tin nhắn trong sidebar
      
      if (messages.length > maxSidebarMessages) {
        console.log(`Cleaning up chat sidebar (${messages.length} > ${maxSidebarMessages})`);
        // Tạo một tin nhắn thông báo rằng lịch sử cũ đã bị xóa để tăng hiệu suất
        const noticeDiv = document.createElement("div");
        noticeDiv.className = "chat-cleanup-notice";
        noticeDiv.textContent = "Một số tin nhắn cũ đã được xóa để tối ưu hiệu năng";
        noticeDiv.style.textAlign = "center";
        noticeDiv.style.padding = "5px";
        noticeDiv.style.margin = "10px 0";
        noticeDiv.style.fontSize = "0.8rem";
        noticeDiv.style.color = "rgba(255, 255, 255, 0.5)";
        
        // Xóa các tin nhắn cũ (giữ lại 30 tin nhắn mới nhất)
        for (let i = 0; i < messages.length - 30; i++) {
          if (messages[i] && messages[i].parentNode) {
            messages[i].parentNode.removeChild(messages[i]);
          }
        }
        
        // Thêm thông báo vào đầu chat để người dùng biết lịch sử cũ đã bị xóa
        if (chatBox.firstChild) {
          chatBox.insertBefore(noticeDiv, chatBox.firstChild);
        }
      }
    }
  }
});
