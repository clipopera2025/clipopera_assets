function createSoraForm() {
  const form = FormApp.create('Sora Video Generator');

  form.addTextItem()
      .setTitle('Your Name')
      .setRequired(true);

  form.addTextItem()
      .setTitle('Prompt Description')
      .setHelpText('Describe your cinematic scene')
      .setRequired(true);

  form.addMultipleChoiceItem()
      .setTitle('Generate Video?')
      .setChoiceValues(['Yes', 'No'])
      .setRequired(true);

  Logger.log('Form URL: ' + form.getEditUrl());
}

function onFormSubmit(e) {
  const responses = e.namedValues;
  const shouldGenerate = responses['Generate Video?'][0] === 'Yes';

  if (!shouldGenerate) return;

  const prompt = responses['Prompt Description'][0];

  const payload = {
    prompt: prompt,
    width: 480,
    height: 480,
    n_seconds: 20,
    model: "sora"
  };

  const options = {
    method: 'POST',
    contentType: 'application/json',
    headers: {
      Authorization: 'Bearer YOUR_OPENAI_API_KEY'
    },
    payload: JSON.stringify(payload)
  };

  UrlFetchApp.fetch('https://api.openai.com/v1/video/generations/jobs', options);
}

