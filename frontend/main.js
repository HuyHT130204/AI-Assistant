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
});