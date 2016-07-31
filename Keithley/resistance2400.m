function [I22,V22,t22,R22,T22,R23]= resistance2400(filename,n,s_d,current22,compl22,meas_range_22,nplc22,current23,compl23,meas_range_23,nplc23);

% prepare file to write
file=fopen(filename,'w');
fprintf(file, '%s \t%s \t%s \t%s \t%s \t%s \t%s \t%s \n','I (A)','V (V)','t (s)','R (Omega)','T (^oC)','I_sample (A)','V_sample (V)','R_sample (Omega)');

% logfile entry:
%logfile
logfile=fopen('log.log','a');
fprintf(logfile,['date: ', datestr(now), '\n']);
fprintf(logfile,['filename: ', filename, '\n']);
fprintf(logfile,['sd: ', num2str(s_d) '\n']);
fprintf(logfile,['n: ', num2str(n) '\n']);
fprintf(logfile,['current: ', num2str(current22) '\n']);
fprintf(logfile,['compl: ', num2str(compl22) '\n']);
fprintf(logfile,['meas_range_2400: ', num2str(meas_range_22) '\n']);
fprintf(logfile,['nplc: ', num2str(nplc22) '\n']);
fprintf(logfile,['current_sample: ', num2str(current23) '\n']);
fprintf(logfile,['compl_sample: ', num2str(compl23) '\n']);
fprintf(logfile,['meas_range_2400_sample: ', num2str(meas_range_23) '\n']);
fprintf(logfile,['nplc_sample: ', num2str(nplc23) '\n']);
fprintf(logfile,'\n');
fclose(logfile);

% Create a GPIB object. 2400:k22
obj1 = instrfind('Type', 'gpib', 'BoardIndex', 0, 'PrimaryAddress', 22, 'Tag', '');
% Create the GPIB object if it does not exist
% otherwise use the object that was found.
if isempty(obj1)
    obj1 = gpib('Keithley', 0, 22);
% Set the property values.
set(obj1, 'BoardIndex', 0);
set(obj1, 'ByteOrder', 'littleEndian');
set(obj1, 'BytesAvailableFcn', '');
set(obj1, 'BytesAvailableFcnCount', 48);
set(obj1, 'BytesAvailableFcnMode', 'eosCharCode');
set(obj1, 'CompareBits', 8);
set(obj1, 'EOIMode', 'on');
set(obj1, 'EOSCharCode', 'LF');
set(obj1, 'EOSMode', 'read&write');
set(obj1, 'ErrorFcn', '');
set(obj1, 'InputBufferSize', 10000);
set(obj1, 'Name', 'GPIB0-22');
set(obj1, 'OutputBufferSize', 10000);
set(obj1, 'OutputEmptyFcn', '');
set(obj1, 'PrimaryAddress', 22);
set(obj1, 'RecordDetail', 'compact');
set(obj1, 'RecordMode', 'overwrite');
set(obj1, 'RecordName', 'record.txt');
set(obj1, 'SecondaryAddress', 0);
set(obj1, 'Tag', '');
set(obj1, 'Timeout', 60);
set(obj1, 'TimerFcn', '');
set(obj1, 'TimerPeriod', 1);
set(obj1, 'UserData', []);
else
    fclose(obj1);
    obj1 = obj1(1);
end
if nargout > 0 
    out1 = [obj1]; 
end

% Create a GPIB object. 2400:k23
obj2 = instrfind('Type', 'gpib', 'BoardIndex', 0, 'PrimaryAddress', 23, 'Tag', '');

% Create the GPIB object if it does not exist
% otherwise use the object that was found.
if isempty(obj2)
    obj2 = gpib('Keithley', 0, 23);
% Set the property values.
set(obj2, 'BoardIndex', 0);
set(obj2, 'ByteOrder', 'littleEndian');
set(obj2, 'BytesAvailableFcn', '');
set(obj2, 'BytesAvailableFcnCount', 48);
set(obj2, 'BytesAvailableFcnMode', 'eosCharCode');
set(obj2, 'CompareBits', 8);
set(obj2, 'EOIMode', 'on');
set(obj2, 'EOSCharCode', 'LF');
set(obj2, 'EOSMode', 'read&write');
set(obj2, 'ErrorFcn', '');
set(obj2, 'InputBufferSize', 10000);
set(obj2, 'Name', 'GPIB0-23');
set(obj2, 'OutputBufferSize', 10000);
set(obj2, 'OutputEmptyFcn', '');
set(obj2, 'PrimaryAddress', 23);
set(obj2, 'RecordDetail', 'compact');
set(obj2, 'RecordMode', 'overwrite');
set(obj2, 'RecordName', 'record.txt');
set(obj2, 'SecondaryAddress', 0);
set(obj2, 'Tag', '');
set(obj2, 'Timeout', 60);
set(obj2, 'TimerFcn', '');
set(obj2, 'TimerPeriod', 1);
set(obj2, 'UserData', []);
else
    fclose(obj2);
    obj2 = obj2(1);
end
if nargout > 0 
    out2 = [obj2]; 
end
%------------------------------------------------------
% end create instruments
%------------------------------------------------------
fopen(obj1);
fprintf(obj1,':ABORT');
fprintf(obj1,':*RST');
fprintf(obj1,':ROUT:TERM REAR'); %rear terminal
fprintf(obj1,':SYST:BEEP:STAT OFF'); %beep off
fprintf(obj1,':SYST:RSEN ON'); % 4-wire sensing on
fprintf(obj1,':SOUR:CLE:AUTO OFF');
fprintf(obj1,':SENS:FUNC:CONC OFF');
fprintf(obj1,':SOUR:FUNC CURR');
fprintf(obj1,':SENSE:FUNC ''VOLT:DC''');
fprintf(obj1,':SOUR:CURR:MODE FIX');
fprintf(obj1,[':SENS:VOLT:PROT ' num2str(compl22)]); % current compliance
fprintf(obj1,[':SENS:VOLT:RANG ' num2str(meas_range_22)]); % current measurement range
fprintf(obj1,[':SENS:CURR:NPLC ' num2str(nplc22)]);
fprintf(obj1,':FORM:ELEM:SENS VOLT, CURR, TIME');
fprintf(obj1,':SYST:TIME:RES:AUTO ON');
fopen(obj2);
fprintf(obj2,':ABORT');
fprintf(obj2,':*RST');
fprintf(obj2,':ROUT:TERM REAR'); %rear terminal
fprintf(obj2,':SYST:BEEP:STAT OFF'); %beep off
fprintf(obj2,':SYST:RSEN ON'); % 4-wire sensing on off
fprintf(obj2,':SOUR:CLE:AUTO OFF');
fprintf(obj2,':SENS:FUNC:CONC OFF');
fprintf(obj2,':SOUR:FUNC CURR');
fprintf(obj2,':SENSE:FUNC ''VOLT:DC''');
fprintf(obj2,':SOUR:CURR:MODE FIX');
fprintf(obj2,[':SENS:VOLT:PROT ' num2str(compl23)]); % current compliance
fprintf(obj2,[':SENS:VOLT:RANG ' num2str(meas_range_23)]); % current measurement range
fprintf(obj2,[':SENS:CURR:NPLC ' num2str(nplc23)]);
fprintf(obj2,':FORM:ELEM:SENS VOLT, CURR, TIME');
fprintf(obj2,':SYST:TIME:RES:AUTO ON');
%measurement 
%------------------------------------------------------
fprintf(obj1,':OUTP ON');
fprintf(obj2,':OUTP ON');
fprintf(obj1,[':SOUR:CURR:LEV ' num2str(current22)]);
fprintf(obj2,[':SOUR:CURR:LEV ' num2str(current23)]);
I22=zeros(1,n);
V22=zeros(1,n);
t22=zeros(1,n);
R22=zeros(1,n);
T22=zeros(1,n);
I23=zeros(1,n);
V23=zeros(1,n);
R23=zeros(1,n);
tic;
for i=1:n;
    %% main measurement cycle:
    % take a reading with the K2400
    data22 = query(obj1, ':READ?');
    t22(1,i)=toc;
    I22(1,i)=str2double(data22(15:27));
    V22(1,i)=str2double(data22(1:13));
    R22(1,i)=V22(1,i)/I22(1,i);
    alpha=3.85e-3;
    R0=1000;
    T22(1,i)=(R22(1,i)/R0 -1)/alpha;
    %% take sample reading
    data23 = query(obj2, ':READ?');
    I23(1,i)=str2double(data23(15:27));
    V23(1,i)=str2double(data23(1:13));
    R23(1,i)=V23(1,i)/I23(1,i);
    fprintf(file, '%12.8E \t%12.8E \t%12.8E \t%12.8E \t%12.8E  \t%12.8E  \t%12.8E  \t%12.8E \n',I22(1,i),V22(1,i),t22(1,i),R22(1,i),T22(1,i),I23(1,i),V23(1,i),R23(1,i));
    fprintf('%d of %d done: \t%12.8E \t%12.8E  \t%12.8E \n',i,n,t22(1,i),T22(1,i),R23(1,i));
    %plot(t(1,i),V(1,i)./I(1,i),'o'); hold on;
    pause(s_d);
end
pause(1);
fprintf(obj2,':OUTP OFF');
fprintf(obj1,':OUTP OFF');
fclose(obj2);
fclose(obj1);
delete(obj2);
delete(obj1);
clear obj2;
clear obj1;