export interface UserData {
  name: string;
  surname: string;
  birthday: string;
  gender: string;
  mail: string;
  phone_num: string;
  password: string;
}

export async function registerUser(data: UserData): Promise<any> {
  const url = 'http://etbx.ru:7070/register';
  
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