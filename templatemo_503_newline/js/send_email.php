<?php
header('Content-Type: text/plain');

// POST 방식으로 데이터가 전송되었는지 확인
if ($_SERVER['REQUEST_METHOD'] === 'POST') {

    // 'suggestion' 키의 데이터가 있는지 확인
    if (isset($_POST['suggestion'])) {
        $suggestion = htmlspecialchars($_POST['suggestion']);

        // 이메일 설정
        $to      = 'ygim0472@gmail.com';
        $subject = '웹사이트 건의문이 도착했습니다';
        $message = "새로운 건의문:\n\n" . $suggestion;
        $headers = 'From: webmaster@example.com' . "\r\n" .
                   'Reply-To: webmaster@example.com' . "\r\n" .
                   'X-Mailer: PHP/' . phpversion();

        // 메일 전송
        if (mail($to, $subject, $message, $headers)) {
            echo "성공적으로 건의문을 보냈습니다.";
        } else {
            echo "메일 전송에 실패했습니다.";
        }
    } else {
        echo "건의문 내용이 없습니다.";
    }
} else {
    echo "유효하지 않은 요청 방식입니다.";
}
?>