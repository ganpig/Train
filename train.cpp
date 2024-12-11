#include <bits/stdc++.h>
#define INDEPENDANT 0

int maxPlanCount;

int readTime(std::istream &fin) {
    std::string strTime;
    fin >> strTime;
    int h, m;
    sscanf(strTime.c_str(), "%d%*c%d", &h, &m);
    return h * 60 + m;
}

std::string time2str(int time) {
    std::stringstream ss;
    if (time >= 1440)
        ss << time / 1440 << ':';
    ss << std::setw(2) << std::setfill('0') << time / 60 % 24 << ':' << std::setw(2) << std::setfill('0') << time % 60;
    return ss.str();
}

struct Train {
    struct Stop {
        int id, arrive, leave;
        float price;
    };
    std::string name;
    std::vector<Stop> stops;
};
std::vector<Train> trains;
std::map<std::string, int> staId;
std::vector<std::string> staName;

struct Plan {
    int id, time;
    float price;
    std::vector<std::array<int, 3>> path;
    friend bool operator<(Plan a, Plan b) { return a.time != b.time ? a.time < b.time : a.price < b.price; }
    operator int() { return time; }
    Plan(int _id, int _time) : id(_id), time(_time), price(0) {}
    Plan(int _id, int _time, Plan pre, int train, int stop, int __time) {
        id = _id;
        time = _time;
        price = pre.price;
        path = pre.path;
        path.push_back({train, stop, __time});
    }
    void update(int _id, int _time, float _price) {
        if (_price <= 0)
            std::cout << _id;
        id = _id, time += _time, price += _price;
    }
};

struct Plans {
    std::vector<Plan> x;
    friend Plans merge(Plans a, Plans b) {
        std::vector<Plan> tmp, res;
        std::merge(a.x.begin(), a.x.end(), b.x.begin(), b.x.end(), std::back_inserter(tmp));
        float minPrice = 1e9;
        int minCount = 1e9;
        for (auto &plan : tmp)
            if (plan.price < minPrice || plan.price == minPrice && plan.path.size() < minCount)
                minPrice = plan.price, minCount = plan.path.size(), res.push_back(plan);
        if (res.size() > maxPlanCount) {
            std::vector<Plan> ress;
            for (int i = 0; i < maxPlanCount; i++)
                ress.push_back(res[1. * i / (maxPlanCount - 1) * (res.size() - 1) + 0.5]);
            return {ress};
        }
        return {res};
    }
};

void init() {
    std::ifstream fin("trains.txt");
    int N;
    fin >> N;
    trains.resize(N);
    for (auto &[name, stops] : trains) {
        fin >> name;
        int c;
        fin >> c;
        stops.resize(c);
        for (auto &stop : stops) {
            std::string stopName;
            fin >> stopName;
            if (!staId.count(stopName))
                staId[stopName] = staName.size(), staName.push_back(stopName);
            stop.id = staId[stopName];
            stop.arrive = readTime(fin);
            stop.leave = readTime(fin);
            if (stop.arrive > stop.leave) // 停站期间经过零点
                stop.leave += 1440;
            int day;
            fin >> day;
            stop.arrive += 1440 * (day - 10); // 必须为负数
            stop.leave += 1440 * (day - 10);
            fin >> stop.price;
        }
    }
    std::cerr << "数据读取完毕，共有" << staName.size() << "个车站，" << trains.size() << "个车次。\n";
}

Plans query(std::string departure, std::string destination, bool depPre, bool desPre, int startTime, int minTransTime, int maxTransCount) {
    std::vector<Plans> dis(staName.size());
    if (depPre) {
        for (int i = 0; i < staName.size(); i++)
            if (staName[i].substr(0, departure.size()) == departure)
                dis[i] = {{{i, startTime - minTransTime}}};
    } else
        dis[staId[departure]] = {{{staId[departure], startTime - minTransTime}}};

#if !INDEPENDANT
    std::cout << (maxTransCount + 1) * trains.size() << std::endl;
#endif

    for (int transCount = 0; transCount <= maxTransCount; transCount++) {
        std::cerr << "正在计算换乘" << transCount << "次的方案……";
        auto begin = clock();
        auto newdis = dis;
        for (int i = 0; i < trains.size(); i++) {
#if !INDEPENDANT
            int process = transCount * trains.size() + i;
            if (process % 100 == 0)
                std::cout << process << std::endl;
#endif
            auto &[name, stops] = trains[i];
            Plans now;
            for (int j = 0; j < stops.size(); j++) {
                for (auto &plan : now.x)
                    plan.update(stops[j].id, stops[j].arrive - stops[j - 1].arrive, stops[j].price - stops[j - 1].price);
                newdis[stops[j].id] = merge(newdis[stops[j].id], now);
                for (auto &plan : dis[stops[j].id].x) {
                    if (!plan.path.empty() && plan.path.back()[0] == i)
                        continue;
                    auto readyTime = plan;
                    readyTime.time += minTransTime;
                    int day = (readyTime - stops[j].leave - 1) / 1440 + 1;
                    auto newPlan = Plan(stops[j].id, stops[j].arrive + day * 1440, readyTime, i, j, stops[j].leave + day * 1440);
                    now = merge(now, {{newPlan}});
                }
            }
        }
        dis = newdis;
        auto end = clock();
        std::cerr << "耗时" << std::fixed << std::setprecision(3) << 1. * (end - begin) / CLOCKS_PER_SEC << "秒\n";
    }

#if !INDEPENDANT
    std::cout << (maxTransCount + 1) * trains.size() << std::endl;
#endif

    if (desPre) {
        Plans res;
        for (int i = 0; i < staName.size(); i++)
            if (staName[i].substr(0, destination.size()) == destination)
                res = merge(res, dis[i]);
        return res;
    } else
        return dis[staId[destination]];
}

int main(int argc, char **argv) {
    init();

#if INDEPENDANT

    std::cerr << "出发地（后加*启用前缀匹配）：";
    std::string departure;
    bool depPre;
    while (true) {
        std::cin >> departure;
        depPre = false;
        if (departure.back() == '*') {
            departure.pop_back(), depPre = true;
            auto it = staId.lower_bound(departure);
            if (it != staId.end() && it->first.substr(0, departure.size()) == departure)
                break;
        } else if (staId.count(departure))
            break;
        std::cerr << "找不到该车站，请重新输入：";
    }

    std::cerr << "目的地（后加*启用前缀匹配）：";
    std::string destination;
    bool desPre;
    while (true) {
        std::cin >> destination;
        desPre = false;
        if (destination.back() == '*') {
            destination.pop_back(), desPre = true;
            auto it = staId.lower_bound(destination);
            if (it != staId.end() && it->first.substr(0, destination.size()) == destination)
                break;
        } else if (staId.count(destination))
            break;
        std::cerr << "找不到该车站，请重新输入：";
    }

    std::cerr << "出发时间：";
    int startTime = readTime(std::cin);

    std::cerr << "换乘预留时间：";
    int minTransTime;
    std::cin >> minTransTime;

    std::cerr << "最多换乘次数：";
    int maxTransCount;
    std::cin >> maxTransCount;

    std::cerr << "最多方案数：";
    std::cin >> maxPlanCount;

    auto ans = query(departure, destination, depPre, desPre, startTime, minTransTime, maxTransCount);

    if (ans.x.empty()) {
        std::cout << "无可行方案！";
        return 0;
    }

    for (int i = 0; i < ans.x.size(); i++) {
        auto &plan = ans.x[i];
        std::cout << "\n方案" << i + 1 << " 用时" << time2str(plan.time - plan.path[0][2]) << " 约" << plan.price << "元\n";
        for (int j = 0; j < plan.path.size(); j++) {
            auto [train, stop, time] = plan.path[j];
            int onStop = trains[train].stops[stop].id;
            int offStop, offTime;
            if (j == plan.path.size() - 1)
                offStop = plan.id, offTime = plan.time;
            else {
                auto [train_, stop_, time_] = plan.path[j + 1];
                offStop = trains[train_].stops[stop_].id;
                for (auto x : trains[train].stops)
                    if (x.id == offStop) {
                        offTime = time + x.arrive - trains[train].stops[stop].leave;
                        break;
                    }
            }
            std::cout << j + 1 << ": " << trains[train].name << ' ' << time2str(time) << ' ' << staName[onStop] << "->" << staName[offStop] << ' ' << time2str(offTime) << '\n';
        }
    }

#else

    maxPlanCount = atoi(argv[8]);
    auto ans = query(argv[1], argv[2], atoi(argv[3]), atoi(argv[4]), atoi(argv[5]), atoi(argv[6]), atoi(argv[7]));
    std::cout << ans.x.size() << '\n';
    for (auto &plan : ans.x) {
        std::cout << plan.path.size() << ' ' << plan.price << '\n';
        for (int i = 0; i < plan.path.size(); i++) {
            auto [train, stop, time] = plan.path[i];
            int onStop = trains[train].stops[stop].id;
            int offStop, offTime;
            if (i == plan.path.size() - 1)
                offStop = plan.id, offTime = plan.time;
            else {
                auto [train_, stop_, time_] = plan.path[i + 1];
                offStop = trains[train_].stops[stop_].id;
                for (auto x : trains[train].stops)
                    if (x.id == offStop) {
                        offTime = time + x.arrive - trains[train].stops[stop].leave;
                        break;
                    }
            }
            std::cout << trains[train].name << ' ' << time << ' ' << offTime;
            for (int j = stop;; j++) {
                int id = trains[train].stops[j].id;
                std::cout << ' ' << staName[id];
                if (id == offStop)
                    break;
            }
            std::cout << '\n';
        }
    }
#endif
}