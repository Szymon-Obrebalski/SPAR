document.getElementById('order-form').addEventListener('submit', async function(e) {
  e.preventDefault();
  const orderid = parseInt(document.getElementById('orderid').value);
  try {
    const response = await fetch('/store', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ orderid: orderid })
    });
    if (response.ok) {
      alert('Order sent successfully!');
    } else {
      alert('Error sending order!');
    }
  } catch (error) {
    console.error('Fetch error:', error);
    alert('Error sending order!');
  }
});

document.getElementById('upload-form').addEventListener('submit', async function(e) {
  e.preventDefault(); // Prevent default form submission

  const calendarid = document.getElementById('calendarid').value;
  try {
    const response = await fetch('/upload', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ calendarid: calendarid })
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    alert('Upload successful!');
  } catch (error) {
    console.error('Fetch error:', error);
    alert('Error during upload!');
  }
});
