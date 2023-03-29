public function actionIndex()
    {
        $client_id = 'ggNpYwRl3RTl1KACYkBBz3';
        $api_url = 'https://notify-bot.line.me/oauth/authorize?';
        $callback_url = 'http://localhost/yii2-maekha/web/index.php?r=site/callback';

        $query = [
            'response_type' => 'code',
            'client_id' => $client_id,
            'redirect_uri' => $callback_url,
            'scope' => 'notify',
            'state' => 'mylinenotify'
        ];

        $result = $api_url . http_build_query($query);

        return $this->render('line',[
            'result' => $result
        ]);
    }