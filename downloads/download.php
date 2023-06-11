<?php
if(isset($_GET['filename'])) {
    $filename = $_GET['filename'];
    $filePath = 'uploads/' . $filename;

    // Проверяем, существует ли файл
    if(file_exists($filePath)) {
        // Устанавливаем заголовки для скачивания файла
        header('Content-Description: File Transfer');
        header('Content-Type: application/octet-stream');
        header('Content-Disposition: attachment; filename="' . $filename . '"');
        header('Expires: 0');
        header('Cache-Control: must-revalidate');
        header('Pragma: public');
        header('Content-Length: ' . filesize($filePath));

        // Отправляем содержимое файла пользователю
        ob_clean();  // Очищаем буфер вывода
        flush();     // Сбрасываем буфер вывода
        readfile($filePath);
        exit;
    } else {
        echo "Файл не найден.";
    }
}
?>
