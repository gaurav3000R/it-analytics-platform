"use client";

import { useEffect, useState } from 'react';
import Image from "next/image";

export default function Home() {
  const [message, setMessage] = useState('');

  useEffect(() => {
    fetch('http://localhost:8000/api/hello')
      .then(response => response.json())
      .then(data => {
        setMessage(JSON.stringify(data));
      });
  }, []);

  return (
    <div className="font-sans grid grid-rows-[20px_1fr_20px] items-center justify-items-center min-h-screen p-8 pb-20 gap-16 sm:p-20">
      <div className="text-center">
        <p className="text-lg font-semibold">Message from the backend:</p>
        <p className="text-xl">{message}</p>
      </div>
    </div>
  );
}
