export interface UserLogData {
  email: string;
  password: string;
}

export async function loginUser(data: UserLogData): Promise<any> {
  const url = 'http://etbx.ru:7070/login';
  try {
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(data)
    });

    if (!response.ok) {
      return null;
    }

    const result = await response.json();
    localStorage.setItem('mailServiceToken', result.Token)
    return result;
  } catch (error) {
    return null;
  }
}