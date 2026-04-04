import { Cpu } from 'lucide-react';

interface SimHPCLogoProps {
  className?: string;
}

export function SimHPCLogo({ className = 'w-8 h-8' }: SimHPCLogoProps) {
  return <Cpu className={`${className} text-cyan-400`} />;
}
