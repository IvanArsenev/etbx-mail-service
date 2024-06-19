export default interface UserAuth {
  username: string;
  password: string;
}

export interface UserObject {
  id: number;
  username: string;
  lastDate: string;
  lastTheme: string;
}

export interface ThemeObject {
  id: number;
  name: string;
  lastMail: string;
  numberOfAttechments: number | null;
  lastMessageDate: string;
}

export const themes: ThemeObject[][] = [
  [
    {
      id: 1,
      name: 'theme 1',
      lastMail: 'last mail 1',
      numberOfAttechments: 2,
      lastMessageDate: '01.01.2024',
    },
    {
      id: 2,
      name: 'theme 2',
      lastMail: 'last mail 2',
      numberOfAttechments: null,
      lastMessageDate: '01.01.2024',
    },
    {
      id: 3,
      name: 'theme 3',
      lastMail: 'last mail 3',
      numberOfAttechments: 0,
      lastMessageDate: '01.01.2024',
    },
  ],
  [
    {
      id: 1,
      name: 'theme 11212',
      lastMail: 'last mail 1',
      numberOfAttechments: 20,
      lastMessageDate: '01.01.2024',
    },
    {
      id: 2,
      name: 'theme 21313',
      lastMail: 'last mail 2',
      numberOfAttechments: null,
      lastMessageDate: '01.01.2024',
    },
    {
      id: 3,
      name: 'theme 3214123',
      lastMail: 'last mail 3',
      numberOfAttechments: 0,
      lastMessageDate: '01.01.2024',
    },
  ],
]